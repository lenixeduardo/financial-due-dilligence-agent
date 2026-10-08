"""Provision accounts locally. Example: python -m backend.scripts.create_user ..."""
import argparse
import getpass
from app.db import initialize_database,ensure_workspace
from app.user_auth import create_user

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",required=True)
    parser.add_argument("--username",required=True)
    parser.add_argument("--role",choices=["reader","analyst","reviewer","admin"],required=True)
    args=parser.parse_args()
    password=getpass.getpass("Password (minimum 14 characters): ")
    initialize_database()
    ensure_workspace(args.workspace)
    create_user(workspace_id=args.workspace,username=args.username,password=password,role=args.role)
    print("Local account provisioned:",args.username,args.role)
if __name__=="__main__":
    main()
