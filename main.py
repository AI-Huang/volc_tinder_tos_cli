import sys
from pathlib import Path

from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.shortcuts import button_dialog, input_dialog, radiolist_dialog

_SRC_DIR = Path(__file__).resolve().parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from volc_tinder_tos_cli.settings import tos_settings
from volc_tinder_tos_cli.storage.tos_service import TosService

MENU_ACTIONS = [
    ("list_buckets", "List Buckets"),
    ("create_bucket", "Create Bucket"),
    ("delete_bucket", "Delete Bucket"),
    ("list_objects", "List Objects in Bucket"),
    ("upload_object", "Upload Object"),
    ("download_object", "Download Object"),
    ("delete_object", "Delete Object"),
    ("quit", "Quit"),
]

STATUS_PAGE_LINES = 40


def build_main_text(status_text, status_page):
    status_lines = (status_text or "Ready").splitlines() or ["Ready"]
    total_pages = max(
        1, (len(status_lines) + STATUS_PAGE_LINES - 1) // STATUS_PAGE_LINES
    )
    status_page = max(0, min(status_page, total_pages - 1))
    start = status_page * STATUS_PAGE_LINES
    end = start + STATUS_PAGE_LINES
    visible_status_lines = status_lines[start:end]

    lines = ["Choose an operation"]
    lines.append("")
    lines.append("Status")
    lines.append("-" * 48)
    lines.append("\n".join(visible_status_lines))
    lines.append("")
    lines.append(
        f"Page {status_page + 1}/{total_pages} (shortcuts: n/PgDn next, p/PgUp prev)"
    )
    return "\n".join(lines), status_page


def set_status_text(value):
    select_action.status_text = value or "Ready"
    select_action.status_page = 0


def move_status_page(step):
    status_lines = (select_action.status_text or "Ready").splitlines() or ["Ready"]
    total_pages = max(
        1, (len(status_lines) + STATUS_PAGE_LINES - 1) // STATUS_PAGE_LINES
    )
    if total_pages <= 1:
        return
    select_action.status_page = max(
        0, min(select_action.status_page + step, total_pages - 1)
    )


def prompt_text(title, text):
    value = input_dialog(title=title, text=text).run()
    if value is None:
        return None
    value = value.strip()
    return value or None


def select_action():
    buttons = [(label, action) for action, label in MENU_ACTIONS]
    main_text, clamped_page = build_main_text(
        select_action.status_text, select_action.status_page
    )
    select_action.status_page = clamped_page
    app = button_dialog(
        title="volc-tinder-tos-cli",
        text=main_text,
        buttons=buttons,
    )

    status_kb = KeyBindings()

    @status_kb.add("n")
    @status_kb.add("pagedown")
    def _status_next(event):
        event.app.exit(result="status_next")

    @status_kb.add("p")
    @status_kb.add("pageup")
    def _status_prev(event):
        event.app.exit(result="status_prev")

    app.key_bindings = merge_key_bindings([app.key_bindings, status_kb])
    return app.run()


select_action.status_text = "Ready"
select_action.status_page = 0


def select_bucket(tos_service, title, text):
    buckets = tos_service.list_buckets()
    if not buckets:
        set_status_text("No buckets found")
        return None

    values = [(bucket, bucket) for bucket in buckets]
    return radiolist_dialog(title=title, text=text, values=values).run()


def select_object(tos_service, bucket_name, title, text):
    objects = tos_service.list_objects(bucket_name)
    if not objects:
        set_status_text(f"No objects in '{bucket_name}'")
        return None

    values = [(obj, obj) for obj in objects]
    return radiolist_dialog(title=title, text=text, values=values).run()


def confirm_dangerous_action(action_label, target_label, target_value):
    confirmation = input_dialog(
        title="Confirm Destructive Action",
        text=(
            f"WARNING: You are about to {action_label} '{target_value}'.\n"
            "This action cannot be undone.\n\n"
            f"Type {target_label} exactly to confirm:"
        ),
    ).run()
    if confirmation is None or confirmation.strip() != target_value:
        set_status_text("Operation cancelled")
        return False
    return True


def list_buckets(tos_service):
    buckets = tos_service.list_buckets()
    if buckets:
        lines = [f"{index}. {bucket}" for index, bucket in enumerate(buckets, 1)]
        set_status_text("\n".join(lines))
    else:
        set_status_text("No buckets found")


def create_bucket(tos_service):
    bucket_name = prompt_text("Create Bucket", "Enter bucket name:")
    if not bucket_name:
        set_status_text("Bucket name cannot be empty")
        return

    success = tos_service.create_bucket(bucket_name)
    if success:
        set_status_text(f"Bucket '{bucket_name}' created successfully")
    else:
        set_status_text(f"Failed to create bucket '{bucket_name}'")


def delete_bucket(tos_service):
    bucket_name = select_bucket(
        tos_service, "Delete Bucket", "Select the bucket to delete"
    )
    if not bucket_name:
        return

    if not confirm_dangerous_action("delete bucket", "the bucket name", bucket_name):
        return

    success = tos_service.delete_bucket(bucket_name)
    if success:
        set_status_text(f"Bucket '{bucket_name}' deleted successfully")
    else:
        set_status_text(f"Failed to delete bucket '{bucket_name}'")


def list_objects(tos_service):
    bucket_name = select_bucket(
        tos_service, "List Objects", "Select a bucket to inspect"
    )
    if not bucket_name:
        return

    objects = tos_service.list_objects(bucket_name)
    if not objects:
        set_status_text(f"No objects in '{bucket_name}'")
        return

    lines = [f"Bucket: {bucket_name}", ""]
    lines.extend(f"- {obj}" for obj in objects)
    set_status_text("\n".join(lines))


def upload_object(tos_service):
    bucket_name = select_bucket(
        tos_service, "Upload Object", "Select a bucket for the new object"
    )
    if not bucket_name:
        return

    object_key = prompt_text("Upload Object", "Enter object key:")
    content = prompt_text("Upload Object", "Enter object content:")
    if not object_key or not content:
        set_status_text("Object key and content cannot be empty")
        return

    success = tos_service.put_object(bucket_name, object_key, content)
    if success:
        set_status_text(f"Object '{object_key}' uploaded successfully")
    else:
        set_status_text(f"Failed to upload object '{object_key}'")


def download_object(tos_service):
    bucket_name = select_bucket(
        tos_service, "Download Object", "Select a bucket to read from"
    )
    if not bucket_name:
        return

    object_key = select_object(
        tos_service,
        bucket_name,
        "Download Object",
        "Select the object to download",
    )
    if not object_key:
        if select_action.status_text.startswith("No objects in"):
            return
        set_status_text("Download cancelled")
        return

    content = tos_service.get_object(bucket_name, object_key)
    if content is None:
        set_status_text(f"Failed to get object '{object_key}'")
        return

    if isinstance(content, bytes):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            content = content.decode("utf-8", errors="replace")

    set_status_text(f"Bucket: {bucket_name}\nKey: {object_key}\n\n{content}")


def delete_object(tos_service):
    bucket_name = select_bucket(
        tos_service, "Delete Object", "Select a bucket for object deletion"
    )
    if not bucket_name:
        return

    object_key = select_object(
        tos_service,
        bucket_name,
        "Delete Object",
        "Select the object to delete",
    )
    if not object_key:
        if select_action.status_text.startswith("No objects in"):
            return
        set_status_text("Delete cancelled")
        return

    if not confirm_dangerous_action("delete object", "the object key", object_key):
        return

    success = tos_service.delete_object(bucket_name, object_key)
    if success:
        set_status_text(f"Object '{object_key}' deleted successfully")
    else:
        set_status_text(f"Failed to delete object '{object_key}'")


def main():
    tos_service = TosService(
        tos_settings.access_key,
        tos_settings.secret_access_key,
        tos_settings.endpoint,
        tos_settings.region,
    )
    handlers = {
        "list_buckets": list_buckets,
        "create_bucket": create_bucket,
        "delete_bucket": delete_bucket,
        "list_objects": list_objects,
        "upload_object": upload_object,
        "download_object": download_object,
        "delete_object": delete_object,
    }

    while True:
        action = select_action()
        if action in (None, "quit"):
            break
        if action == "status_prev":
            move_status_page(-1)
            continue
        if action == "status_next":
            move_status_page(1)
            continue
        handlers[action](tos_service)


if __name__ == "__main__":
    main()
