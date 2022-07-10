from datetime import datetime

from beanie import WriteRules

from node.enums import MessageType
from node.models import database, request


async def get_pool(identifier: str) -> database.Pool | None:
    return (await database.Pool.find_one(database.Pool.address == identifier, fetch_links=True)) or (
        await database.Pool.find_one(database.Pool.tag == identifier, fetch_links=True)
    )


async def get_public_pools() -> list[database.Pool]:
    pools = await database.Pool.find(database.Pool.public == True, fetch_links=True).to_list()  # noqa
    return pools


async def get_signature(uuid: str) -> database.Signature:
    return await database.Signature.find_one(database.Signature.uuid == uuid)


async def write_message_to_pool(
    pool: database.Pool,
    message_type: MessageType,
    message: request.RequestNewMessage,
    signature: database.Signature,
) -> database.PlaintextMessage | database.EncryptedMessage:
    id = len(pool.messages) + 1  # noqa
    date = datetime.now()

    match message_type:
        case MessageType.plaintext:
            db_message = database.PlaintextMessage(
                type=message_type, id=id, date=date, signature=signature, plaintext=message.plaintext
            )
        case MessageType.encrypted:
            db_message = database.EncryptedMessage(
                type=message_type,
                id=id,
                date=date,
                signature=signature,
                AES_ciphertext=message.AES_ciphertext,
                AES_nonce=message.AES_nonce,
                AES_tag=message.AES_tag,
            )
        case _:
            raise ValueError("Invalid message type.")
    pool.messages.append(db_message)
    await pool.save(link_rule=WriteRules.WRITE)
    return db_message
