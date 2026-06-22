from services.tos_service import TosService
from settings import TOS_ACCESS_KEY, TOS_SECRET_ACCESS_KEY, TOS_ENDPOINT, TOS_REGION


def test_bucket_operations():
    tos_service = TosService(
        TOS_ACCESS_KEY, TOS_SECRET_ACCESS_KEY, TOS_ENDPOINT, TOS_REGION
    )

    bucket_name = "leapwatt-images"
    object_key = "test.txt"
    content = "text"

    print(f"=== Testing bucket: {bucket_name} ===")

    print("\n1. Listing objects in bucket...")
    objects = tos_service.list_objects(bucket_name)
    if objects:
        print(f"   Objects found: {len(objects)}")
        for obj in objects[:5]:
            print(f"   - {obj}")
        if len(objects) > 5:
            print(f"   ... and {len(objects) - 5} more")
    else:
        print("   No objects found")

    print("\n2. Uploading test.txt with content 'text'...")
    success = tos_service.put_object(bucket_name, object_key, content)

    if success:
        print("\n3. Downloading test.txt...")
        downloaded_content = tos_service.get_object(bucket_name, object_key)
        if downloaded_content is not None:
            print(f"   Downloaded content: '{downloaded_content}'")
            if downloaded_content == content:
                print("   ✅ Content matches!")
            else:
                print("   ❌ Content mismatch!")

    print("\n4. Final object list...")
    objects = tos_service.list_objects(bucket_name)
    if object_key in objects:
        print(f"   ✅ test.txt is in the bucket")
    else:
        print(f"   ❌ test.txt not found in bucket")


if __name__ == "__main__":
    test_bucket_operations()
