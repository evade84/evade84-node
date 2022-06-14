from datetime import datetime

from beanie import WriteRules
from node.models import db


async def get_pool(identifier: str) -> db.Pool | None:
    return (await db.Pool.find_one(db.Pool.address == identifier)) or (
        await db.Pool.find_one(db.Pool.tag == identifier)
    )


async def get_public_pools() -> list[db.Pool]:
    pools = await db.Pool.find(db.Pool.public == True).to_list()  # noqa
    return pools


async def pool_exists(identifier: str) -> bool:
    return bool(await get_pool(identifier))


async def get_signature(tag: str) -> db.Signature:
    return await db.Signature.find_one(db.Signature.tag == tag)


async def signature_exists(tag: str) -> bool:
    return bool(await get_signature(tag))


async def write_message_to_pool(
    pool: db.Pool,
    text: str,
    signature: db.Signature | None,
    hide_message_date: bool | None,
) -> db.Message:
    id = len(pool.messages) + 1  # noqa
    message = db.Message(
        id=id,
        text=text,
        signature=signature,
        date=datetime.now() if not hide_message_date else None,
    )
    pool.messages.append(message)
    await pool.save(link_rule=WriteRules.WRITE)
    return message
