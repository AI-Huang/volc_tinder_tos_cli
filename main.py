from prompt_toolkit.shortcuts import button_dialog, input_dialog, radiolist_dialog

from services.tos_service import TosService
from settings import TOS_ACCESS_KEY, TOS_SECRET_ACCESS_KEY, TOS_ENDPOINT, TOS_REGION

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


def build_main_text(status_text):
    lines = ["Choose an operation"]
    lines.append("")
    lines.append("Status")
    lines.append("-" * 48)
    lines.append(status_text or "Ready")
    return "\n".join(lines)


def prompt_text(title, text):
    value = input_dialog(title=title, text=text).run()
    if value is None:
        return None
    value = value.strip()
    return value or None


def select_action():
    buttons = [(label, action) for action, label in MENU_ACTIONS]
    return button_dialog(
        title="volc-tinder-tos-cli",
        text=build_main_text(select_action.status_text),
        buttons=buttons,
    ).run()


select_action.status_text = "Ready"


def select_bucket(tos_service, title, text):
    buckets = tos_service.list_buckets()
    if not buckets:
        select_action.status_text = "No buckets found"
        return None

    values = [(bucket, bucket) for bucket in buckets]
    return radiolist_dialog(title=title, text=text, values=values).run()


def select_object(tos_service, bucket_name, title, text):
    objects = tos_service.list_objects(bucket_name)
    if not objects:
        select_action.status_text = f"No objects in '{bucket_name}'"
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
        select_action.status_text = "Operation cancelled"
        return False
    return True


def list_buckets(tos_service):
    buckets = tos_service.list_buckets()
    if buckets:
        lines = [f"{index}. {bucket}" for index, bucket in enumerate(buckets, 1)]
        select_action.status_text = "\n".join(lines)
    else:
        select_action.status_text = "No buckets found"


def create_bucket(tos_service):
    bucket_name = prompt_text("Create Bucket", "Enter bucket name:")
    if not bucket_name:
        select_action.status_text = "Bucket name cannot be empty"
        return

    success = tos_service.create_bucket(bucket_name)
    if success:
        select_action.status_text = f"Bucket '{bucket_name}' created successfully"
    else:
        select_action.status_text = f"Failed to create bucket '{bucket_name}'"


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
        select_action.status_text = f"Bucket '{bucket_name}' deleted successfully"
    else:
        select_action.status_text = f"Failed to delete bucket '{bucket_name}'"


def list_objects(tos_service):
    bucket_name = select_bucket(
        tos_service, "List Objects", "Select a bucket to inspect"
    )
    if not bucket_name:
        return

    objects = tos_service.list_objects(bucket_name)
    if not objects:
        select_action.status_text = f"No objects in '{bucket_name}'"
        return

    preview = objects[:20]
    lines = [f"Bucket: {bucket_name}", ""]
    lines.extend(f"- {obj}" for obj in preview)
    if len(objects) > len(preview):
        lines.append("")
        lines.append(f"... and {len(objects) - len(preview)} more")
    select_action.status_text = "\n".join(lines)


def upload_object(tos_service):
    bucket_name = select_bucket(
        tos_service, "Upload Object", "Select a bucket for the new object"
    )
    if not bucket_name:
        return

    object_key = prompt_text("Upload Object", "Enter object key:")
    content = prompt_text("Upload Object", "Enter object content:")
    if not object_key or not content:
        select_action.status_text = "Object key and content cannot be empty"
        return

    success = tos_service.put_object(bucket_name, object_key, content)
    if success:
        select_action.status_text = f"Object '{object_key}' uploaded successfully"
    else:
        select_action.status_text = f"Failed to upload object '{object_key}'"


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
        select_action.status_text = "Download cancelled"
        return

    content = tos_service.get_object(bucket_name, object_key)
    if content is None:
        select_action.status_text = f"Failed to get object '{object_key}'"
        return

    if isinstance(content, bytes):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            content = content.decode("utf-8", errors="replace")

    select_action.status_text = f"Bucket: {bucket_name}\nKey: {object_key}\n\n{content}"


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
        select_action.status_text = "Delete cancelled"
        return

    if not confirm_dangerous_action("delete object", "the object key", object_key):
        return

    success = tos_service.delete_object(bucket_name, object_key)
    if success:
        select_action.status_text = f"Object '{object_key}' deleted successfully"
    else:
        select_action.status_text = f"Failed to delete object '{object_key}'"


def main():
    tos_service = TosService(
        TOS_ACCESS_KEY, TOS_SECRET_ACCESS_KEY, TOS_ENDPOINT, TOS_REGION
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
        handlers[action](tos_service)


if __name__ == "__main__":
    main()
