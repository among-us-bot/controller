"""
Created by Epic at 11/13/20
"""
from os import environ as env

owner_ids = env["OWNER_IDS"].split(" ")


class CheckError(Exception):
    pass


def create_check(check_func, name):
    def inner(func):
        current_checks = getattr(func, "__command_checks__", [])
        current_checks.append((check_func, name))
        func.__command_checks__ = current_checks
        return func

    return inner


owner_check = create_check(lambda ctx: ctx.message.author["id"] in owner_ids, "owner_check")
staff_check = create_check(
    lambda ctx: ctx.client.get_config(ctx.message.guild_id).get("config-role") in ctx.message.member["roles"],
    "staff_check")
