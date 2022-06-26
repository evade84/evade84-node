from datetime import datetime

from beanie import WriteRules
from node.models import db, request


async def get_pool(identifier: str) -> db.Pool | None:
    return (await db.Pool.find_one(db.Pool.address == identifier)) or (
        await db.Pool.find_one(db.Pool.tag == identifier)
    )


# async def get_public_pools() -> list[db.Pool]:
#     pools = await db.Pool.find(db.Pool.public == True).to_list()  # noqa
#     return pools


# async def pool_exists(identifier: str) -> bool:
#     return bool(await get_pool(identifier))


async def get_signature(uuid: str) -> db.Signature:
    return await db.Signature.find_one(db.Signature.uuid == uuid)


async def write_message_to_pool(
    pool: db.Pool, message: request.NewMessage, signature: db.Signature
) -> db.Message:
    id = len(pool.messages) + 1  # noqa
    db_message = db.Message(
        id=id,
        date=datetime.now(),
        plaintext=message.plaintext,
        AES_ecnrypted=message.AES_encrypted,
        AES_ciphertext=message.AES_ciphertext,
        AES_nonce=message.AES_nonce,
        AES_tag=message.AES_tag,
        signature=signature,
    )
    pool.messages.append(db_message)
    await pool.save(link_rule=WriteRules.WRITE)
    return db_message
