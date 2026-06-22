from services.tos_service import TosService
from settings import TOS_ACCESS_KEY, TOS_SECRET_ACCESS_KEY, TOS_ENDPOINT, TOS_REGION

if __name__ == "__main__":
    tos_service = TosService(
        TOS_ACCESS_KEY, TOS_SECRET_ACCESS_KEY, TOS_ENDPOINT, TOS_REGION
    )

    print("=== TOS Service Demo ===")
    print("1. List Buckets")
    print("2. Create Bucket")
    print("3. Delete Bucket")
    print("4. List Objects in Bucket")
    print("5. Upload Object")
    print("6. Download Object")
    print("7. Delete Object")

    try:
        choice = int(input("\nEnter your choice (1-7): "))

        if choice == 1:
            buckets = tos_service.list_buckets()
            if buckets:
                print("\nAvailable buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"{i}. {bucket}")
            else:
                print("No buckets found")

        elif choice == 2:
            bucket_name = input("Enter bucket name to create: ").strip()
            if bucket_name:
                tos_service.create_bucket(bucket_name)
            else:
                print("Bucket name cannot be empty")

        elif choice == 3:
            buckets = tos_service.list_buckets()
            if not buckets:
                print("No buckets found")
            else:
                print("\nAvailable buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"{i}. {bucket}")

                try:
                    idx = int(input("\nEnter the number of the bucket to delete: "))
                    if 1 <= idx <= len(buckets):
                        bucket_name = buckets[idx - 1]
                        confirm = (
                            input(
                                f"Are you sure you want to delete '{bucket_name}'? (yes/no): "
                            )
                            .strip()
                            .lower()
                        )
                        if confirm == "yes":
                            tos_service.delete_bucket(bucket_name)
                        else:
                            print("Operation cancelled")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")

        elif choice == 4:
            buckets = tos_service.list_buckets()
            if not buckets:
                print("No buckets found")
            else:
                print("\nAvailable buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"{i}. {bucket}")

                try:
                    idx = int(input("\nEnter the number of the bucket: "))
                    if 1 <= idx <= len(buckets):
                        bucket_name = buckets[idx - 1]
                        objects = tos_service.list_objects(bucket_name)
                        if objects:
                            print(f"\nObjects in {bucket_name}:")
                            for obj in objects[:10]:
                                print(f"- {obj}")
                            if len(objects) > 10:
                                print(f"... and {len(objects) - 10} more")
                        else:
                            print(f"No objects in {bucket_name}")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")

        elif choice == 5:
            buckets = tos_service.list_buckets()
            if not buckets:
                print("No buckets found")
            else:
                print("\nAvailable buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"{i}. {bucket}")

                try:
                    idx = int(input("\nEnter the number of the bucket: "))
                    if 1 <= idx <= len(buckets):
                        bucket_name = buckets[idx - 1]
                        object_key = input("Enter object key: ").strip()
                        content = input("Enter object content: ").strip()
                        if object_key and content:
                            tos_service.put_object(bucket_name, object_key, content)
                        else:
                            print("Object key and content cannot be empty")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")

        elif choice == 6:
            buckets = tos_service.list_buckets()
            if not buckets:
                print("No buckets found")
            else:
                print("\nAvailable buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"{i}. {bucket}")

                try:
                    idx = int(input("\nEnter the number of the bucket: "))
                    if 1 <= idx <= len(buckets):
                        bucket_name = buckets[idx - 1]
                        object_key = input("Enter object key: ").strip()
                        if object_key:
                            content = tos_service.get_object(bucket_name, object_key)
                            if content is not None:
                                print(f"\nObject content:\n{content}")
                            else:
                                print("Failed to get object")
                        else:
                            print("Object key cannot be empty")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")

        elif choice == 7:
            buckets = tos_service.list_buckets()
            if not buckets:
                print("No buckets found")
            else:
                print("\nAvailable buckets:")
                for i, bucket in enumerate(buckets, 1):
                    print(f"{i}. {bucket}")

                try:
                    idx = int(input("\nEnter the number of the bucket: "))
                    if 1 <= idx <= len(buckets):
                        bucket_name = buckets[idx - 1]
                        object_key = input("Enter object key to delete: ").strip()
                        if object_key:
                            tos_service.delete_object(bucket_name, object_key)
                        else:
                            print("Object key cannot be empty")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")

        else:
            print("Invalid choice")

    except ValueError:
        print("Invalid input")
