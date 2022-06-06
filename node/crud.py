from node.models import db


async def get_pool(identifier: str) -> db.Pool | None:
    return (await db.Pool.find_one(db.Pool.address == identifier)) or (
        await db.Pool.find_one(db.Pool.tag == identifier)
    )


async def write_message(pool: db.Pool, text: str, signature: str | None) -> db.Message:
    index = len(pool.messages)
    message = db.Message(index=index, text=text, signature=signature)
    pool.messages.append(message)
    await pool.save()
    return message


async def read_messages(pool: db.Pool, count) -> list[db.Message]:
    messages = pool.messages[::-1][:count]
    return messages[::-1]
