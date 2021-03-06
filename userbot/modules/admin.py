from asyncio import sleep
from os import remove
from telethon.errors import BadRequestError, ChatAdminRequiredError, ImageProcessFailedError, PhotoCropSizeSmallError, UserAdminInvalidError
from telethon.errors.rpcerrorlist import UserIdInvalidError, MessageTooLongError
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest, InviteToChannelRequest)
from telethon.tl.functions.messages import (UpdatePinnedMessageRequest, AddChatUserRequest)
from telethon.tl.types import (PeerChannel, ChannelParticipantsAdmins,
                               ChatAdminRights, ChatBannedRights,
                               MessageEntityMentionName, MessageMediaPhoto,
                               ChannelParticipantsBots, User, InputPeerChat)
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.events import ChatAction
from userbot import BOTLOG, BOTLOG_CHATID, BRAIN_CHECKER, CMD_HELP, bot, WARN_MODE, WARN_LIMIT, WHITELIST, ALIVE_NAME
from userbot.events import register
from userbot.main import PLUGIN_MESAJLAR
from userbot.cmdhelp import CmdHelp
import datetime, telethon

from userbot.language import get_value
LANG = get_value("admin")

PP_TOO_SMOL = LANG['PP_TOO_SMOL']
PP_ERROR = LANG['PP_ERROR']
NO_ADMIN = LANG['NO_ADMIN']
NO_PERM = LANG['NO_PERM']
NO_SQL = LANG['NO_SQL']

CHAT_PP_CHANGED = LANG['CHAT_PP_CHANGED']
CHAT_PP_ERROR = LANG['CHAT_PP_ERROR']
INVALID_MEDIA = LANG['INVALID_MEDIA']

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)


async def elcjn(brend):
    args = brend.pattern_match.group(1).split(':', 1)
    extra = None
    if brend.reply_to_msg_id and not len(args) == 2:
        previous_message = await brend.get_reply_message()
        user_obj = await brend.client.get_entity(previous_message.from_id)
        extra = brend.pattern_match.group(1)
    elif len(args[0]) > 0:
        user = args[0]
        if len(args) == 2:
            extra = args[1]
        if user.isnumeric():
            user = int(user)
        if not user:
            await brend.edit(f"`{ALIVE_NAME}`: **??stifad????i ad??,id yaz??n v?? ya istifad????iy?? cavab verin!**")
            return
        if brend.message.entities is not None:
            probable_user_mention_entity = brend.message.entities[0]
            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await brend.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await brend.client.get_entity(user)
        except Exception as err:
            return await brend.edit("U??ursuzluq \n **X??TA???**\n", str(err))
    return user_obj, extra


async def get_user_from_id(user, brend):
    if isinstance(user, str):
        user = int(user)
    try:
        user_obj = await brend.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await brend.edit(str(err))
        return None
    return user_obj

try:
    from userbot import client2, client3
except BaseException:
    client2 = client3 = None


@register(outgoing=True, pattern=r"^\.gkick(?: |$)(.*)")
async def elcjn(brend):
    lazy = brend
    sender = await lazy.get_sender()
    me = await lazy.client.get_me()
    if not sender.id == me.id:
        rkp = await lazy.reply("`Qruplar axtar??l??r...`")
    else:
        rkp = await lazy.edit("`Prosses ba??lad??...`")
    me = await brend.client.get_me()
    await rkp.edit(f"**??stifad????i qruplardan at??l??r..**")
    my_mention = "[{}](tg://user?id={})".format(me.first_name, me.id)
    f"@{me.username}" if me.username else my_mention
    await brend.get_chat()
    a = b = 0
    if brend.is_private:
        user = brend.chat
        reason = brend.pattern_match.group(1)
    else:
        brend.chat.title
    try:
        user, reason = await get_user_from_brend(brend)
    except BaseException:
        pass
    try:
        if not reason:
            reason = 'Private'
    except BaseException:
        return await rkp.edit("**X??TA???! Nam??lum istifad????i.**")
    if user:
        if user.id == WHITELIST:
            return await rkp.edit(LANG['BRAIN'])
        try:
            await brend.client(BlockRequest(user))
            await brend.client(UnblockRequest(user))
        except BaseException:
            pass
        testrk = [d.entity.id for d in await brend.client.get_dialogs() if (d.is_group or d.is_channel)]
        for i in testrk:
            try:
                await brend.client.edit_permissions(i, user, view_messages=False)
                await brend.client.edit_permissions(i, user, send_messages=True)
                a += 1
                await rkp.edit(f"**??stifad????i qruplardan at??l??r!\n????xar??ld?? {a} qrupdan.....**")

            except BaseException:
                b += 1
    else:
        await rkp.edit(f"**??stifad????iy?? cavab ver!**")

    return await rkp.edit(f"**??stifad????i : [{user.first_name}](tg://user?id={user.id}) {a} qrupdan ????xar??ld??**")

@register(outgoing=True, pattern="^.gban(?: |$)(.*)")
async def gbanspider(gspdr):

    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await gspdr.edit(NO_ADMIN)
        return

    try:
        from userbot.modules.sql_helper.gban_sql import gban
    except:
        await gspdr.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(gspdr)
    if user:
        pass
    else:
        return

    if user.id in BRAIN_CHECKER or user.id in WHITELIST:
        await gspdr.edit(LANG['BRAIN'])
        return

    await gspdr.edit(LANG['BANNING'])
    if gban(user.id) == False:
        await gspdr.edit(
            LANG['ALREADY_GBANNED'])
    else:
        if reason:
            await gspdr.edit(f"{LANG['GBANNED_REASON']} {reason}")
        else:
            await gspdr.edit(LANG['GBANNED'])

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID, "#GBAN\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {gspdr.chat.title}(`{gspdr.chat_id}`)")


@register(incoming=True)
async def gbanmsg(moot):
                            
    try:
        from userbot.modules.sql_helper.gban_sql import is_gbanned
    except:
        return

    gbanned = is_gbanned(str(moot.sender_id))
    if gbanned == str(moot.sender_id):
        try:
            chat = await moot.get_chat()
        except:
            return
            
        if (type(chat) == User):
            return 

        admin = chat.admin_rights
        creator = chat.creator

        if not admin and not creator:
            return

        try:
            await moot.client(EditBannedRequest(moot.chat_id, moot.sender_id,
                                            BANNED_RIGHTS))
            await moot.reply(LANG['GBAN_TEXT'])
        except:
            return

@register(outgoing=True, pattern="^.ungban(?: |$)(.*)")
async def ungban(un_gban):

    chat = await un_gban.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await un_gban.edit(NO_ADMIN)
        return

    try:
        from userbot.modules.sql_helper.gban_sql import ungban
    except:
        await un_gban.edit(NO_SQL)
        return

    user = await get_user_from_event(un_gban)
    user = user[0]
    if user:
        pass
    else:
        return

    await un_gban.edit(LANG['UNGBANNING'])

    if ungban(user.id) is False:
        await un_gban.edit(LANG['NO_BANNED'])
    else:

        await un_gban.edit(LANG['UNGBANNED'])

        if BOTLOG:
            await un_gban.client.send_message(
                BOTLOG_CHATID, "#UNGBAN\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {un_gban.chat.title}(`{un_gban.chat_id}`)")


@register(outgoing=True, pattern="^.setgpic$")
async def set_group_photo(gpic):
                             
    if not gpic.is_group:
        await gpic.edit(LANG['PRIVATE'])
        return
    replymsg = await gpic.get_reply_message()
    chat = await gpic.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    photo = None

    if not admin and not creator:
        await gpic.edit(NO_ADMIN)
        return

    if replymsg and replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await gpic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split('/'):
            photo = await gpic.client.download_file(replymsg.media.document)
        else:
            await gpic.edit(INVALID_MEDIA)

    if photo:
        try:
            await gpic.client(
                EditPhotoRequest(gpic.chat_id, await
                                 gpic.client.upload_file(photo)))
            await gpic.edit(CHAT_PP_CHANGED)

        except PhotoCropSizeSmallError:
            await gpic.edit(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await gpic.edit(PP_ERROR)


@register(outgoing=True, pattern="^.promote(?: |$)(.*)")
async def promote(promt):
                             
    chat = await promt.get_chat()

    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await promt.edit(NO_ADMIN)
        return

    new_rights = ChatAdminRights(invite_users=True,
                                 change_info=True,
                                 delete_messages=True,
                                 pin_messages=True,)
    try:
        await promt.edit(LANG['PROMOTING'])
    except:
        await promt.reply(LANG['PROMOTING'])
    user, rank = await get_user_from_event(promt)
    if not rank:
        rank = "??dar????i"
    if user:
        pass
    else:
        return
                             
    try:
        await promt.client(
            EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await promt.edit(LANG['SUCCESS_PROMOTE'])

    except:
        await promt.edit(NO_PERM)
        return

    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID, "#NORMAL_??DAR??????_ETM??K\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {promt.chat.title}(`{promt.chat_id}`)")

@register(outgoing=True, pattern="^.propromote(?: |$)(.*)")
async def propromote(propromote):
                             
    chat = await propromote.get_chat()

    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await propromote.edit(NO_ADMIN)
        return

    new_rights = ChatAdminRights(add_admins=True,
                                 invite_users=True,
                                 change_info=True,
                                 ban_users=True,
                                 delete_messages=True,
                                 pin_messages=True,
                                 manage_call=True)
    try:
        await propromote.edit(LANG['PROMOTING'])
    except:
        await propromote.reply(LANG['PROMOTING'])
    user, rank = await get_user_from_event(propromote)
    if not rank:
        rank = "PRO ??dar????i"
    if user:
        pass
    else:
        return
                             
    try:
        await propromote.client(
            EditAdminRequest(propromote.chat_id, user.id, new_rights, rank))
        await propromote.edit(LANG['SUCCESS_PROPROMOTE'])

    except:
        await propromote.edit(NO_PERM)
        return

    if BOTLOG:
        await propromote.client.send_message(
            BOTLOG_CHATID, "#PRO_??DAR??????_ETM??K\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {propromote.chat.title}(`{propromote.chat_id}`)")


@register(outgoing=True, pattern="^.demote(?: |$)(.*)")
async def demote(dmod):
                             
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await dmod.edit(NO_ADMIN)
        return

    try:
        await dmod.edit(LANG['UNPROMOTING'])
    except:
        await dmod.reply(LANG['UNPROMOTING'])
    rank = "brend"
    user = await get_user_from_event(dmod)
    user = user[0]
    if user:
        pass
    else:
        return

    newrights = ChatAdminRights(add_admins=None,
                                invite_users=None,
                                change_info=None,
                                ban_users=None,
                                delete_messages=None,
                                pin_messages=None)
                             
    try:
        await dmod.client(
            EditAdminRequest(dmod.chat_id, user.id, newrights, rank))

    except:
        await dmod.edit(NO_PERM)
        return
    await dmod.edit(LANG['UNPROMOTE'])

    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID, "#ADM??NL??K-ALINMASI\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {dmod.chat.title}(`{dmod.chat_id}`)")

@register(outgoing=True, pattern="^.ban(?: |$)(.*)")
async def ban(bon):

    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await bon.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(bon)
    if user:
        pass
    else:
        return

    if user.id in BRAIN_CHECKER or user.id in WHITELIST:
        await bon.edit(
            LANG['BRAIN']
        )
        return

    await bon.edit(LANG['BANNING'])

    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id,
                                           BANNED_RIGHTS))
    except:
        await bon.edit(NO_PERM)
        return
                             
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except:
        await bon.edit(
            LANG['NO_PERM_BUT_BANNED'])
        return
                             
    SONMESAJ = PLUGIN_MESAJLAR['ban'].format(
        id = user.id,
        username = '@' + user.username if user.username else f"[{user.first_name}](tg://user?id={user.id})",
        first_name = user.first_name,
        last_name = '' if not user.last_name else user.last_name,
        mention = f"[{user.first_name}](tg://user?id={user.id})",
        date = datetime.datetime.strftime(datetime.datetime.now(), '%c'),
        count = (chat.participants_count - 1) if chat.participants_count else 'Bilinmiyor'
    )
    
    if reason:
        await bon.edit(f"{SONMESAJ}\n{LANG['REASON']}: {reason}")
    else:
        await bon.edit(SONMESAJ)
                       
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID, "#BAN\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {bon.chat.title}(`{bon.chat_id}`)")


@register(outgoing=True, pattern="^.unban(?: |$)(.*)")
async def nothanos(unbon):

    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await unbon.edit(NO_ADMIN)
        return

    await unbon.edit(LANG['UNBANNING'])

    user = await get_user_from_event(unbon)
    user = user[0]
    if user:
        pass
    else:
        return

    try:
        await unbon.client(
            EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await unbon.edit(LANG['UNBANNED'].format(
            id = user.id,
            username = '@' + user.username if user.username else f"[{user.first_name}](tg://user?id={user.id})",
            first_name = user.first_name,
            last_name = '' if not user.last_name else user.last_name,
            mention = f"[{user.first_name}](tg://user?id={user.id})",
            date = datetime.datetime.strftime(datetime.datetime.now(), '%c'),
            count = (chat.participants_count) if chat.participants_count else 'Bilinmir'
        ))

        if BOTLOG:
            await unban.client.send_message(
                BOTLOG_CHATID, "#UNBAN\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {unbon.chat.title}(`{unbon.chat_id}`)")
    except:
        await unbon.edit(LANG['EXCUSE_ME_WTF'])


@register(outgoing=True, pattern="^.mute(?: |$)(.*)")
async def spider(spdr):
                       
    try:
        from userbot.modules.sql_helper.spam_mute_sql import mute
    except:
        await spdr.edit(NO_SQL)
        return

    chat = await spdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await spdr.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(spdr)
    if user:
        pass
    else:
        return

    if user.id in BRAIN_CHECKER or user.id in WHITELIST:
        await spdr.edit(
            LANG['BRAIN']
        )
        return

    self_user = await spdr.client.get_me()

    if user.id == self_user.id:
        await spdr.edit(
            LANG['NO_MUTE_ME'])
        return

    await spdr.edit(LANG['MUTING'])
    if mute(spdr.chat_id, user.id) is False:
        return await spdr.edit(LANG['ALREADY_MUTED'])
    else:
        try:
            await spdr.client(
                EditBannedRequest(spdr.chat_id, user.id, MUTE_RIGHTS))

            await mutmsg(spdr, user, reason, chat)
        except UserAdminInvalidError:
            await mutmsg(spdr, user, reason, chat)
        except:
            return await spdr.edit(LANG['WTF_MUTE'])

async def mutmsg(spdr, user, reason, chat):
    SONMESAJ = PLUGIN_MESAJLAR['mute'].format(
            id = user.id,
            username = '@' + user.username if user.username else f"[{user.first_name}](tg://user?id={user.id})",
            first_name = user.first_name,
            last_name = '' if not user.last_name else user.last_name,
            mention = f"[{user.first_name}](tg://user?id={user.id})",
            date = datetime.datetime.strftime(datetime.datetime.now(), '%c'),
            count = (chat.participants_count) if chat.participants_count else 'Bilinmiyor'
        )

    if reason:
        await spdr.edit(f"{SONMESAJ}\n{LANG['REASON']}: {reason}")
    else:
        await spdr.edit(f"{SONMESAJ}")

    if BOTLOG:
        await spdr.client.send_message(
            BOTLOG_CHATID, "#MUTE\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {spdr.chat.title}(`{spdr.chat_id}`)")


@register(outgoing=True, pattern="^.unmute(?: |$)(.*)")
async def unmoot(unmot):

    chat = await unmot.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await unmot.edit(NO_ADMIN)
        return

    try:
        from userbot.modules.sql_helper.spam_mute_sql import unmute
    except:
        await unmot.edit(NO_SQL)
        return

    await unmot.edit(LANG['UNMUTING'])
    user = await get_user_from_event(unmot)
    user = user[0]
    if user:
        pass
    else:
        return

    if unmute(unmot.chat_id, user.id) is False:
        return await unmot.edit(LANG['ALREADY_UNMUTED'])
    else:

        try:
            await unmot.client(
                EditBannedRequest(unmot.chat_id, user.id, UNBAN_RIGHTS))
            await unmot.edit(LANG['UNMUTED'].format(
            id = user.id,
            username = '@' + user.username if user.username else f"[{user.first_name}](tg://user?id={user.id})",
            first_name = user.first_name,
            last_name = '' if not user.last_name else user.last_name,
            mention = f"[{user.first_name}](tg://user?id={user.id})",
            date = datetime.datetime.strftime(datetime.datetime.now(), '%c'),
            count = (chat.participants_count) if chat.participants_count else 'Bilinmir'
        ))
        except UserAdminInvalidError:
            await unmot.edit(LANG['UNMUTED'].format(
            id = user.id,
            username = '@' + user.username if user.username else f"[{user.first_name}](tg://user?id={user.id})",
            first_name = user.first_name,
            last_name = '' if not user.last_name else user.last_name,
            mention = f"[{user.first_name}](tg://user?id={user.id})",
            date = datetime.datetime.strftime(datetime.datetime.now(), '%c'),
            count = (chat.participants_count) if chat.participants_count else 'Bilinmir'
        ))
        except:
            await unmot.edit(LANG['WTF_MUTE'])
            return

        if BOTLOG:
            await unmot.client.send_message(
                BOTLOG_CHATID, "#UNMUTE\n"
                f"??ST??FAD??C??: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {unmot.chat.title}(`{unmot.chat_id}`)")


@register(incoming=True)
async def muter(moot):
                        
    try:
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
    except:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                try:
                    await moot.client(
                        EditBannedRequest(moot.chat_id, moot.sender_id, rights))
                except:
                    pass
    if gmuted:
        for i in gmuted:
            if i.sender == str(moot.sender_id):
                await moot.delete()

@register(outgoing=True, pattern="^.ungmute(?: |$)(.*)")
async def ungmoot(un_gmute):

    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await un_gmute.edit(NO_ADMIN)
        return

    try:
        from userbot.modules.sql_helper.gmute_sql import ungmute
    except:
        await un_gmute.edit(NO_SQL)
        return

    user = await get_user_from_event(un_gmute)
    user = user[0]
    if user:
        pass
    else:
        return

    await un_gmute.edit(LANG['GUNMUTING'])

    if ungmute(user.id) is False:
        await un_gmute.edit(LANG['NO_GMUTE'])
    else:

        await un_gmute.edit(LANG['UNMUTED'])

        if BOTLOG:
            await un_gmute.client.send_message(
                BOTLOG_CHATID, "#UNGMUTE\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {un_gmute.chat.title}(`{un_gmute.chat_id}`)")


@register(outgoing=True, pattern="^.gmute(?: |$)(.*)")
async def gspider(gspdr):

    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await gspdr.edit(NO_ADMIN)
        return

    try:
        from userbot.modules.sql_helper.gmute_sql import gmute
    except:
        await gspdr.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(gspdr)
    if user:
        pass
    else:
        return

    if user.id in BRAIN_CHECKER or user.id in WHITELIST:
        await gspdr.edit(LANG['BRAIN'])
        return

    await gspdr.edit(LANG['GMUTING'])
    if gmute(user.id) == False:
        await gspdr.edit(
            LANG['ALREADY_GMUTED'])
    else:
        if reason:
            await gspdr.edit(f"{LANG['GMUTED']} {LANG['REASON']}: {reason}")
        else:
            await gspdr.edit(LANG['GMUTED'])

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID, "#GMUTE\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {gspdr.chat.title}(`{gspdr.chat_id}`)")

@register(outgoing=True, pattern="^.check(?: |$)(.*)", groups_only=False)
@register(outgoing=True, pattern="^.qrupuyoxla(?: |$)(.*)", groups_only=False)
async def rm_deletedacc(show):

    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = LANG['NO_ZOMBIE']

    if con != "sil":
        await show.edit(LANG['ZOMBIE'])
        async for user in show.client.iter_participants(show.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = LANG['ZOMBIES'].format(del_u)
        await show.edit(del_status)
        return

    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await show.edit(LANG['NO_ADMIN'])
        return

    await show.edit(LANG['CLEANING'])
    del_u = 0
    del_a = 0

    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS))
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            except:
                await show.edit(LANG['NO_BAN_YT'])
                return
            await show.client(
                EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"**{del_u}** {LANG['DELETED']}"

    if del_a > 0:
        del_status = f"**{del_u}** {LANG['DELETED']} \
        \n**{del_a}** ??d??d silin??n admin hesab??n?? ????xara bilm??dim"

    await show.edit(del_status)
    await sleep(2)
    await show.delete()

    if BOTLOG:
        await show.client.send_message(
            BOTLOG_CHATID, "#TEMIZLIK\n"
            f"**{del_u}** ??d??d silinmi?? hesab ????xard??ld?? !!\
            \nQRUP: {show.chat.title}(`{show.chat_id}`)")


@register(outgoing=True, pattern="^.admin$")
async def get_admin(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = f'<b>{title} {LANG["ADMINS"]}:</b> \n'
    try:
        async for user in show.client.iter_participants(
                show.chat_id, filter=ChannelParticipantsAdmins):
            if not user.deleted:
                link = f"<a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                userid = f"<code>{user.id}</code>"
                mentions += f"\n{link} {userid}"
            else:
                mentions += f"\nSilin??n Hesab <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    await show.edit(mentions, parse_mode="html")


@register(outgoing=True, pattern="^.pin(?: |$)(.*)")
async def pin(msg):

    chat = await msg.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await msg.edit(NO_ADMIN)
        return

    to_pin = msg.reply_to_msg_id

    if not to_pin:
        await msg.edit(LANG['NEED_MSG'])
        return

    options = msg.pattern_match.group(1)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await msg.client(
            UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
    except:
        await msg.edit(NO_PERM)
        return

    await msg.edit(LANG['PINNED'])

    user = await get_user_from_id(msg.from_id, msg)

    if BOTLOG:
        await msg.client.send_message(
            BOTLOG_CHATID, "#SABITL??M??\n"
            f"ADM??N: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {msg.chat.title}(`{msg.chat_id}`)\n"
            f"S??SL??: {not is_silent}")


@register(outgoing=True, pattern="^.kick(?: |$)(.*)")
async def kick(usr):
                             
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await usr.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(usr)
    if not user:
        await usr.edit(LANG['NOT_FOUND'])
        return

    if user.id in BRAIN_CHECKER or user.id in WHITELIST:
        await usr.edit(
            LANG['BRAIN']
        )
        return

    await usr.edit(LANG['KICKING'])

    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(.5)
    except Exception as e:
        await usr.edit(NO_PERM + f"\n{str(e)}")
        return

    if reason:
        await usr.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `{LANG['KICKED']}`\n{LANG['REASON']}: {reason}"
        )
    else:
        await usr.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `{LANG['KICKED']}`")

    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID, "#KICK\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {usr.chat.title}(`{usr.chat_id}`)\n")




async def get_user_from_event(event):
    args = event.pattern_match.group(1).split(' ', 1)
    extra = None
    if event.reply_to_msg_id and not len(args) == 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("`??stifad????inin istifad????i ad??n??, ??D v?? ya mesaj??n?? verin!`")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj, extra
        try:
            user_obj = await event.client.get_entity(user)
        except Exception as err:
            await event.edit(str(err))
            return None

    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except Exception as err:
        await event.edit(str(err))
        return None

    return user_obj

@register(outgoing=True, pattern="^.unwarn ?(.*)")
async def unwarn(event):
          
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return

    try:
        import userbot.modules.sql_helper.warn_sql as warn
    except:
        await event.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    await event.edit(LANG['UNWARNING'])
    silme = warn.sil_warn(user.id)
    if silme == False:
        await event.edit(LANG['UNWARNED'])
        return

    warnsayi = warn.getir_warn(user.id)
    
    await event.edit(f"[{user.first_name}](tg://user?id={user.id})`, {LANG['UNWARN']} {warnsayi}/{WARN_LIMIT}`")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#WARN\n"
            f"??stifad????i: [{user.first_name}](tg://user?id={user.id})\n"
            f"Qrup: {event.chat.title}(`{event.chat_id}`)")

@register(outgoing=True, pattern="^.warn ?(.*)")
async def warn(event):
                     
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await event.edit(NO_ADMIN)
        return
                     
    try:
        import userbot.modules.sql_helper.warn_sql as warn
    except:
        await event.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(event)
    if user:
        pass
    else:
        return

    if user.id in BRAIN_CHECKER or user.id in WHITELIST:
        await event.edit(LANG['BRAIN'])
        return
                     
    await event.edit(LANG['WARNING'])
    warn.ekle_warn(user.id)
    warnsayi = warn.getir_warn(user.id)
    if warnsayi >= WARN_LIMIT:
        if WARN_MODE == "gban":
            await Warn_Gban(event, warn, user)
        else:
            await Warn_Gmute(event, warn, user)
        return
    await event.edit(f"[{user.first_name}](tg://user?id={user.id})`, {warnsayi}/{WARN_LIMIT} {LANG['WARN']}`")

    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "#WARN\n"
            f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
            f"QRUP: {event.chat.title}(`{event.chat_id}`)")

async def Warn_Gmute(event, warn, user, reason = None):
    await event.delete()
    yeni = await event.reply(f"`S??n?? b??s q??d??r x??b??rdarl??q etdim!` [{user.first_name}](tg://user?id={user.id})`, indi is?? qlobal olaraq s??ssiz?? al??nd??n!`")

    try:
        from userbot.modules.sql_helper.gmute_sql import gmute
    except:
        await yeni.edit(NO_SQL)
        return
        
    yeni2 = await yeni.reply("`S??ssiz?? al??n??r...`")
        
    if gmute(user.id) == False:
        await yeni2.edit(
            '`X??ta! ??stifad????i onsuzda d??nya s??viyy??sind?? s??ssizdir.`')
    else:
        if reason != None:
            await yeni2.edit(f"??????stifad????i qlobal olaraq s??ssizl????dirildi!\n????S??b??bi: {reason}")
        else:
            await yeni2.edit("??????stifad????i qlobal olaraq s??ssizdir!")

        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID, "#GMUTE\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {event.chat.title}(`{event.chat_id}`)")
    warn.toplu_sil_warn(user.id)

async def Warn_Gban(event, warn, user, reason = None):
    await event.delete()
    yeni = await event.reply(f"????S??n?? b??s q??d??r x??b??rdarl??q etdim [{user.first_name}](tg://user?id={user.id}), indi is?? qlobal olaraq qada??an olundun!`")

    try:
        from userbot.modules.sql_helper.gban_sql import gban
    except:
        await yeni.edit(NO_SQL)
        return
        
    yeni2 = await yeni.reply("??????Qada??an olunur...")
        
    if gban(user.id) == False:
        await yeni2.edit(
            '???X??ta! ??stifad????i onsuzda qlobal olaraq qada??an edilmi??dir.')
    else:
        if reason != None:
            await yeni2.edit(f"??????stifad????i art??q qlobal olaraq qada??an edilmi??dir!\n????S??b??bi: `{reason}`")
        else:
            await yeni2.edit("??????stifad????i art??q qlobal olaraq qada??an edilmi??dir!")

        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID, "#GBAN\n"
                f"??ST??FAD??????: [{user.first_name}](tg://user?id={user.id})\n"
                f"QRUP: {event.chat.title}(`{event.chat_id}`)")
    warn.toplu_sil_warn(user.id)

@register(outgoing=True, pattern="^.bots$", groups_only=True)
async def get_bots(show):
                     
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = f'<b> {title} qrupunda tap??lan botlar:</b>\n'
    try:

        async for user in show.client.iter_participants(
                show.chat_id, filter=ChannelParticipantsBots):
            if not user.deleted:
                link = f"<a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                userid = f"<code>{user.id}</code>"
                mentions += f"\n{link} {userid}"
            else:
                mentions += f"\nSilinmi?? bot <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions, parse_mode="html")
    except MessageTooLongError:
        await show.edit(
            "Uyda! Burada ??ox bot var. Botlar??n siyah??s??n?? bir fayl olaraq g??nd??rir??m.")
        file = open("botlist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "botlist.txt",
            caption='{} qrupunda tap??lan botlar:'.format(title),
            reply_to=show.id,
        )
        remove("botlist.txt")

CmdHelp('admin').add_command(
        'promote', '<istifad????i ad??/cav??blama> <x??susi ad (ist??y?? ba??l??)>', 'Se??diyiniz istifad????iy?? qrupu idar?? icaz??si verir.'
    ).add_command(
        'propromote', '<istifad????i ad??/cav??blama> <x??susi ad (ist??y?? ba??l??)>', 'Se??diyiniz istifad????iy?? qrupu idar?? ??????n pro icaz?? verir.'
    ).add_command(
        'demote', '<istifad????i ad??/cavablama>', 'Se??diyiniz userin idar????ilik icaz??sini alar.'
    ).add_command(
        'ban', '<istifad????i ad??/cavablama> <s??b??b (ist??y?? ba??l??)>', 'Se??diyiniz istifad????inin mesaj yazmas??n?? dayand??rar, idar????il??rd??d?? d?? i??l??yir.'
    ).add_command(
        'unban', '<istifad????i ad??/cavablama>', 'Veril??n qada??an??(ban) qald??r??r.'
    ).add_command(
        'kick', '<istifad????i ad??/cavablama> <s??b??bi (ist??y?? ba??l??)>', 'Qrupdan g??st??rdiyiniz istifad????ini ????xardar.'
    ).add_command(
        'gmute', '<istifad????i ad??/cavablama> <s??b??bi (ist??y?? ba??l??)>', '??stifad????i idar?? etdiyiniz b??t??n qruplarda s??ssiz?? al??n??r.'
    ).add_command(
        'ungmute', '<istifad????i ad??/cavablama>', '??stifad????ini qlobal olaraq s??ssiz?? al??nanlar siyah??s??ndan sil??r.'
    ).add_command(
        'check', None, 'Bir qrupdak?? silinmi?? hesablar?? axtar??r. Qrupdak?? silin??n hesablar?? ????xarmaq ??????n `.ckeck sil` ??mrini istifad?? edin.'
    ).add_command(
        'admin', None, 'S??hb??t idar????il??rinin siyah??s??n?? al??r.'
    ).add_command(
        'bots', None, 'Qrupda olan botlar?? g??st??rir.'
    ).add_command(
        'warn', '<istifad????i ad??/cavablama> <s??b??b (ist??kd??n asl??>', 'G??st??rdiyiniz istifad????iy?? x??b??rdarl??q ed??r.'
    ).add_command(
        'unwarn', '<istifad????i ad??/cavablama> <sebep (iste??e ba??l??>', 'G??st??rdiyiniz istifad????inin x??b??rdarl??????n?? sil??r.'
    ).add_command(
        'warn', '<istifad????i ad??/cavablama> <s??b??b (ist??y?? ba??l??>', 'G??st??rdiyiniz istifad????iy?? x??b??rdarl??q ed??r.'
    ).add_command(
        'gban', '<istifad????i ad??/cavablama>', '??stifad????ini qlobal olaraq qada??an edin.'
    ).add_command(
        'ungban', '<istifad????i ad??/cavablama>', '??stifad????inin qlobal qada??as??n?? qald??r??r.'
    ).add_command(
        'gkick', '<id,isifad????i ad??,yan??t>', '??stifad????ini b??t??n ortaq qruplar??n??zdan ????xarar..'
    ).add_command(
        'pin', '<cavablama>', 'Cavab verdiyiniz mesaj?? sabitl??y??r.'
    ).add_command(
        'setgpic', '<cavablama>', 'Qrup fotosunu d??yi??dirir.'
    ).add()
