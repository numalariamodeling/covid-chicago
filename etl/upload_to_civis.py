#!/usr/bin/env python3

"""This script uploads a file from disk to Civis Platform
and shares it with the appropriate groups, users, and projects.
"""

import argparse

import civis


CIVIS_GROUP_ID = 12553
KEITH_WALEWSKI_USER_ID = 10238
ROBOT_USER_ID = 10037
PROJECT_ID = 135876


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "file_path", help="Path to the file to upload to Civis Platform"
    )
    args = parser.parse_args()
    client = civis.APIClient()
    file_id = civis.io.file_to_civis(
        args.file_path, expires_at=None, client=client
    )
    print(f"Uploaded {args.file_path} as Civis file ID {file_id}")
    client.files.put_shares_groups(file_id, [CIVIS_GROUP_ID], "read")
    client.files.put_shares_users(file_id, [KEITH_WALEWSKI_USER_ID], "read")
    client.files.put_shares_users(file_id, [ROBOT_USER_ID], "manage")
    client.files.put_projects(file_id, PROJECT_ID)


if __name__ == "__main__":
    main()
