import tos


class TosService:
    def __init__(self, ak, sk, endpoint, region):
        self.client = tos.TosClientV2(ak, sk, endpoint, region)

    def create_bucket(self, bucket_name):
        try:
            self.client.create_bucket(bucket_name)
            print(f"Bucket {bucket_name} created successfully")
            return True
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error creating bucket: {e}")
            return False
        except Exception as e:
            print(f"Error creating bucket: {e}")
            return False

    def list_buckets(self):
        try:
            response = self.client.list_buckets()
            return [bucket.name for bucket in response.buckets]
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error listing buckets: {e}")
            return []
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return []

    def list_objects(self, bucket_name, max_keys=1000):
        try:
            marker = None
            objects = []

            while True:
                response = self.client.list_objects(
                    bucket_name, max_keys=max_keys, marker=marker
                )

                if response.contents:
                    objects.extend([obj.key for obj in response.contents])

                if not response.is_truncated:
                    break
                marker = response.next_marker

            return objects
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error listing objects: {e}")
            return []
        except Exception as e:
            print(f"Error listing objects: {e}")
            return []

    def put_object(self, bucket_name, object_key, content):
        try:
            resp = self.client.put_object(bucket_name, object_key, content=content)
            if resp.status_code == 200:
                print(f"Object {object_key} uploaded successfully")
                return True
            else:
                print(
                    f"Failed to upload object {object_key}, status code: {resp.status_code}"
                )
                return False
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error putting object: {e}")
            return False
        except Exception as e:
            print(f"Error putting object: {e}")
            return False

    def get_object(self, bucket_name, object_key):
        try:
            resp = self.client.get_object(bucket_name, object_key)
            return resp.content
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error getting object: {e}")
            return None
        except Exception as e:
            print(f"Error getting object: {e}")
            return None

    def delete_object(self, bucket_name, object_key):
        try:
            resp = self.client.delete_object(bucket_name, object_key)
            if resp.status_code == 204:
                print(f"Object {object_key} deleted successfully")
                return True
            else:
                print(
                    f"Failed to delete object {object_key}, status code: {resp.status_code}"
                )
                return False
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error deleting object: {e}")
            return False
        except Exception as e:
            print(f"Error deleting object: {e}")
            return False

    def delete_bucket(self, bucket_name):
        try:
            marker = None
            deleted_count = 0

            while True:
                response = self.client.list_objects(
                    bucket_name, max_keys=1000, marker=marker
                )

                if not response.contents:
                    if not response.is_truncated:
                        break
                    marker = response.next_marker
                    continue

                objects_to_delete = [
                    tos.models2.ObjectTobeDeleted(key=obj.key)
                    for obj in response.contents
                ]
                self.client.delete_multi_objects(bucket_name, objects_to_delete)
                deleted_count += len(objects_to_delete)

                if response.is_truncated:
                    marker = response.next_marker
                else:
                    break

            if deleted_count > 0:
                print(f"Deleted {deleted_count} objects from bucket {bucket_name}")

            self.client.delete_bucket(bucket_name)
            print(f"Bucket {bucket_name} deleted successfully")
            return True
        except tos.exceptions.TosClientError as e:
            print(f"TOS Error deleting bucket: {e}")
            return False
        except Exception as e:
            print(f"Error deleting bucket: {e}")
            return False
