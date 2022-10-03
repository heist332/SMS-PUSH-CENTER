import discord
import sqlite3
import uuid
import datetime
from datetime import timedelta
import os
import asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed

tokens = "OTExOTU0MTUzOTczMTIxMTI0.YZo5fQ.GqRe17YpXYJxs2VkMHlUb6QNVAw"

client = discord.Client()


def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    if ((ExpireTime - ServerTime).total_seconds() > 0):
        return False
    else:
        return True


def is_guild_valid(id):
    if os.path.isfile(f"database/{str(id)}.db"):
        con = sqlite3.connect(f"database/{str(id)}.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM configs;")
        configs = cur.fetchone()
        con.close()
        if is_expired(configs[0]):
            return (True, False)
        else:
            return (True, True)
    else:
        return (False, False)


@client.event
async def on_ready():
    print("=====READY=====")


@client.event
async def on_message(message):
    if message.content.startswith("!생성 "):
        if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
            days = message.content.split(" ")[1]
            count = message.content.split(" ")[2]
            types = message.content.split(" ")[3]
            if days.isdigit():
                if count.isdigit():
                    if int(days) > 0 and int(count) > 0:
                        codelist = []
                        for codes in range(int(count)):
                            code = "-" + str(uuid.uuid4()).upper()
                            codelist.append(code)
                            con = sqlite3.connect("license.db")
                            cur = con.cursor()
                            cur.execute(
                                "INSERT INTO licenses VALUES(?, ?, ?);", (code, days, types))
                            con.commit()
                        con.close()

                        keys = "\n".join(codelist)
                        await message.author.send(f"라이센스가 생성되었습니다.\n{keys}")
                    else:
                        await message.author.send("날짜, 개수는 0보다 커야합니다.")
                else:
                    await message.author.send("개수는 숫자로만 입력해주세요.")
            else:
                await message.author.send("날짜는 숫자로만 입력해주세요.")

    # ==============생성코드===================

    if message.content.startswith("!등록 "):
        if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
            await message.delete()
            code = message.content.split(" ")[1]
            if code.isdigit():
                await message.author.send("라이센스는 숫자로만 이루어져있지 않습니다.")
            else:
                con = sqlite3.connect("license.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM licenses WHERE key == ?;", (code,))
                key_info = cur.fetchone()
                con.close()
                if key_info == None:
                    await message.author.send("라이센스가 존재하지 않습니다.")
                    return
                else:
                    await message.author.send("잠시만 기다려주세요...")
                    con = sqlite3.connect("license.db")
                    cur = con.cursor()
                    cur.execute(
                        "DELETE FROM licenses WHERE key == ?;", (code,))
                    con.commit()
                    con.close()
                    await message.author.send(f"라이센스 등록이 완료되었습니다.\n[ 등록 성공한 코드 ] : {code}\n[ 기한 ] : {key_info[1]}")
                    con = sqlite3.connect(
                        f"database/{str(message.guild.id)}.db")
                    cur = con.cursor()

                    cur.execute(
                        "CREATE TABLE setting (webhook TEXT, token TEXT, status INTEGER, cool INTEGER);")
                    con.commit()

                    cur.execute(
                        "CREATE TABLE configs (expiringdate TEXT, status INTEGER, cool INTEGER, keyword TEXT);")
                    con.commit()
                    cur.execute("INSERT INTO configs VALUES(?, ?, ?, ?);",
                                ((datetime.datetime.now() + timedelta(days=int(key_info[1]))).strftime('%Y-%m-%d %H:%M'), 0, 0, ""))
                con.commit()
                con.close()

    if message.content.startswith("!키워드"):
        if is_guild_valid(message.guild.id)[0] and is_guild_valid(message.guild.id)[1]:
            if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()
                try:
                    keyword = message.content.split(" ")[1]
                except Exception as e:
                    print(e)
                    await message.channel.send(embed=discord.Embed(title="키워드가 해제되었습니다."))
                    con = sqlite3.connect(
                        f"database/{str(message.guild.id)}.db")
                    cur = con.cursor()

                    cur.execute("UPDATE configs SET keyword = ?;",
                                ("",))
                    con.commit()
                    con.close()
                    return
                con = sqlite3.connect(
                    f"database/{str(message.guild.id)}.db")
                cur = con.cursor()

                cur.execute("UPDATE configs SET keyword = ?;",
                            (str(keyword),))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title=f"키워드가 변경되었습니다.\n위 봇은 이제부터 타이틀이 `{keyword}`인 푸쉬알림을 무시합니다."))

            else:
                await message.channel.send(embed=discord.Embed("당신은 서버 소유주가 아닙니다."))
        else:
            await message.channel.send(embed=discord.Embed(title="라이센스가 등록되지 않은 서버입니다.\n에서 라이센스를 발급해주세요."))

    if message.content.startswith("!설정"):
        if is_guild_valid(message.guild.id)[0] and is_guild_valid(message.guild.id)[1]:
            if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
                await message.channel.send(embed=discord.Embed(title="디엠을 확인해주세요."))
                msg = await message.author.send(embed=discord.Embed(title="알림을 받으실 웹훅을 이 채널에 전송해주세요."))
                try:
                    webhook = await client.wait_for("message", timeout=60, check=lambda m: m.author.id == message.author.id and isinstance(m.channel, discord.channel.DMChannel))
                except asyncio.TimeoutError:
                    await message.author.send(embed=discord.Embed(title="제한시간이 초과되었습니다."))
                    return

                await msg.edit(embed=discord.Embed(title="에서 발급받으신 토큰을 이 채널에 전송해주세요."))
                token = await client.wait_for("message", timeout=60, check=lambda m: m.author.id == message.author.id and isinstance(m.channel, discord.channel.DMChannel))
                await msg.edit(embed=discord.Embed(title="잠시만 기다려주세요."))
                await asyncio.sleep(5)
                con = sqlite3.connect(
                    f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("INSERT INTO setting VALUES(?, ?, ?, ?);",
                            (webhook.content, token.content, 0, 0,))
                con.commit()
                con.close()
                await msg.edit(embed=discord.Embed(title="설정이 완료되었습니다."))
            else:
                await message.channel.send(embed=discord.Embed(title="당신은 서버 소유주가 아닙니다."))
        else:
            await message.channel.send(embed=discord.Embed(title="라이센스가 등록되지 않은 서버입니다.\n에서 라이센스를 발급해주세요."))

    if message.content == "!시작":
        if is_guild_valid(message.guild.id)[0] and is_guild_valid(message.guild.id)[1]:
            if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()

                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM setting;")
                settings = cur.fetchall()
                con.close()

                options = discord.Embed(
                    title="설정 목록", description="설정 목록입니다.")
                br = "\n"

                names = []

                i = 0
                for setting in settings:
                    i = int(i) + 1
                    options.add_field(
                        inline=True, name=f"`{setting[0]}`", value=f"번호 {i}번\n토큰 `{str(setting[1])}`\n현재 상태 `{str(setting[2])}`")
                    names.append(setting[0])

                print(names)

                msgs = await message.channel.send(embed=options)

                try:

                    msges = await client.wait_for("message", timeout=60, check=lambda m: (m.author.id == message.author.id))
                    if not msges.content.isdigit():
                        await message.channel.send("번호는 숫자로만 입력해주세요.")
                        return
                    if int(msges.content) > i or int(msges.content) < 0:
                        await message.channel.send("번호가 알맞지 않습니다.")
                        return
                except asyncio.TimeoutError:
                    try:
                        await msgs.delete()
                    except:
                        pass
                    return

                try:
                    await msgs.delete()
                except Exception as e:
                    print(e)
                    pass
                try:

                    await message.channel.send(f"잠시만 기다려주세요.\n입력하신 번호 : {msges.content}")
                    con = sqlite3.connect(
                        f"database/{str(message.guild.id)}.db")
                    cur = con.cursor()
                    cur.execute(
                        "SELECT * FROM setting WHERE webhook == ?;", (str(names[int(msges.content) - 1]),))
                    setting = cur.fetchone()
                    con.close()

                    con = sqlite3.connect(
                        f"database/{str(message.guild.id)}.db")
                    cur = con.cursor()

                    cur.execute("UPDATE setting SET status = ?, cool = ? WHERE webhook == ?;",
                                (1, 0, str(names[int(msges.content) - 1]),))
                    con.commit()
                    con.close()
                except Exception as e:
                    print(e)

                if int(setting[3]) == 1:
                    await message.channel.send(embed=discord.Embed(title="아직 쿨다운 상태입니다.\n잠시 후 사용해주세요."))
                    return
                if int(setting[2]) == 1:
                    await message.channel.send(embed=discord.Embed(title="이미 푸쉬알림을 파싱중입니다.\n`!중단` 명령어로 중단해주세요."))
                    return

                process = await asyncio.subprocess.create_subprocess_exec("py", 'server.py', "", str(setting[1]), str(message.guild.id), str(names[int(msges.content) - 1]))

                await message.channel.send(embed=discord.Embed(title="알림을 파싱하기 시작했습니다."))

            else:
                await message.channel.send(embed=discord.Embed("당신은 서버 소유주가 아닙니다."))
        else:
            await message.channel.send(embed=discord.Embed(title="라이센스가 등록되지 않은 서버입니다.\n에서 라이센스를 발급해주세요."))

    if message.content == "!중단":
        if is_guild_valid(message.guild.id)[0] and is_guild_valid(message.guild.id)[1]:
            if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()

                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM setting;")
                settings = cur.fetchall()
                con.close()

                options = discord.Embed(
                    title="설정 목록", description="설정 목록입니다.")
                br = "\n"

                names = []

                i = 0
                for setting in settings:
                    i = int(i) + 1
                    options.add_field(
                        inline=True, name=f"`{setting[0]}`", value=f"번호 {i}번\n토큰 `{str(setting[1])}`\n현재 상태 `{str(setting[2])}`")
                    names.append(setting[0])

                print(names)

                msgs = await message.channel.send(embed=options)

                try:

                    msges = await client.wait_for("message", timeout=60, check=lambda m: (m.author.id == message.author.id))
                    if not msges.content.isdigit():
                        await message.channel.send("번호는 숫자로만 입력해주세요.")
                        return
                    if int(msges.content) > i or int(msges.content) < 0:
                        await message.channel.send("번호가 알맞지 않습니다.")
                        return
                except asyncio.TimeoutError:
                    try:
                        await msgs.delete()
                    except:
                        pass
                    return

                try:
                    await msgs.delete()
                except Exception as e:
                    print(e)
                    pass
                try:

                    await message.channel.send(f"잠시만 기다려주세요.\n입력하신 번호 : {msges.content}")
                    con = sqlite3.connect(
                        f"database/{str(message.guild.id)}.db")
                    cur = con.cursor()
                    cur.execute(
                        "SELECT * FROM setting WHERE webhook == ?;", (str(names[int(msges.content) - 1]),))
                    setting = cur.fetchone()

                    cur.execute("UPDATE setting SET status = ?, cool = ? WHERE webhook == ?;",
                                (0, 1, str(names[int(msges.content) - 1]),))
                    con.commit()
                    con.close()
                except Exception as e:
                    print(e)

                await message.channel.send(embed=discord.Embed(title="알림 파싱이 종료되었습니다.\n바로 사용을 원하실 경우 30초후 `!시작` 명령어를 입력해주세요."))
                await asyncio.sleep(30)
                con = sqlite3.connect(
                    f"database/{str(message.guild.id)}.db")
                cur = con.cursor()

                cur.execute("UPDATE setting SET cool = ? WHERE webhook == ?;",
                            (0, str(names[int(msges.content) - 1]),))
                con.commit()
                con.close()
                await message.channel.send(embed=discord.Embed(title="쿨다운 시간이 끝났습니다.\n이제 `!시작` 명령어를 입력해서 바로 사용 가능합니다."))

            else:
                await message.channel.send(embed=discord.Embed("당신은 서버 소유주가 아닙니다."))
        else:
            await message.channel.send(embed=discord.Embed(title="라이센스가 등록되지 않은 서버입니다.\n에서 라이센스를 발급해주세요."))

    if message.content == "!삭제":
        if is_guild_valid(message.guild.id)[0] and is_guild_valid(message.guild.id)[1]:
            if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()

                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM setting;")
                settings = cur.fetchall()
                con.close()

                options = discord.Embed(
                    title="설정 목록", description="설정 목록입니다.")
                br = "\n"

                names = []

                i = 0
                for setting in settings:
                    i = int(i) + 1
                    options.add_field(
                        inline=True, name=f"`{setting[0]}`", value=f"번호 {i}번\n토큰 `{str(setting[1])}`\n현재 상태 `{str(setting[2])}`")
                    names.append(setting[0])

                print(names)

                msgs = await message.channel.send(embed=options)

                try:

                    msges = await client.wait_for("message", timeout=60, check=lambda m: (m.author.id == message.author.id))
                    if not msges.content.isdigit():
                        await message.channel.send("번호는 숫자로만 입력해주세요.")
                        return
                    if int(msges.content) > i or int(msges.content) < 0:
                        await message.channel.send("번호가 알맞지 않습니다.")
                        return
                except asyncio.TimeoutError:
                    try:
                        await msgs.delete()
                    except:
                        pass
                    return

                try:
                    await msgs.delete()
                except Exception as e:
                    print(e)
                    pass
                try:

                    await message.channel.send(f"잠시만 기다려주세요.\n입력하신 번호 : {msges.content}")
                    con = sqlite3.connect(
                        f"database/{str(message.guild.id)}.db")
                    cur = con.cursor()
                    cur.execute(
                        "DELETE FROM setting WHERE webhook == ?;", (str(names[int(msges.content) - 1]),))
                    con.commit()
                    con.close()
                except Exception as e:
                    print(e)

                await message.channel.send(embed=discord.Embed(title="삭제 완료.\n선택하신 설정이 삭제되었습니다."))

            else:
                await message.channel.send(embed=discord.Embed("당신은 서버 소유주가 아닙니다."))
        else:
            await message.channel.send(embed=discord.Embed(title="라이센스가 등록되지 않은 서버입니다.\n에서 라이센스를 발급해주세요."))

    if (message.content.startswith("!서버삭제 ")):
        if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
            serverid = message.content.split(" ")[1]
            file = f'./database/{serverid}.db'
            if os.path.isfile(file):
                os.remove(file)
                print("삭제완료")
                await message.author.send(embed=discord.Embed(title=serverid + ".db\n서버 삭제가 완료되었습니다."))
            else:
                await message.author.send(embed=discord.Embed(title="서버를 찾지 못했습니다."))
        else:
            await message.author.send(embed=discord.Embed(title="관리자가 아닙니다."))

    if message.content == "!서버정보":
        if is_guild_valid(message.guild.id)[0] and is_guild_valid(message.guild.id)[1]:
            if message.author.id == message.guild.owner_id or message.author.id == 839630971086831626 or message.author.id == 905961060933189692:
                await message.channel.send(embed=discord.Embed(title="DM을 확인해주세요."))
                con = sqlite3.connect(f"database/{str(message.guild.id)}.db")
                cur = con.cursor()
                cur.execute("SELECT * FROM configs;")
                configs = cur.fetchone()
                con.close()
                ServerTime = datetime.datetime.now()
                ExpireTime = datetime.datetime.strptime(
                    configs[0], '%Y-%m-%d %H:%M')
                if ((ExpireTime - ServerTime).total_seconds() > 0):
                    how_long = (ExpireTime - ServerTime)
                    days = how_long.days
                    hours = how_long.seconds // 3600
                    minutes = how_long.seconds // 60 - hours * 60
                    time = str(round(days)) + "일 " + str(round(hours)
                                                         ) + "시간 " + str(round(minutes)) + "분"
                else:
                    time = "만료됨"
                embed = discord.Embed(
                    title="서버정보", description=f"{message.guild.name}서버의 서버정보입니다.\n라이센스 만료일 : {ExpireTime}\n라이센스 만료까지 남은시간 : {time}")
                embed.set_thumbnail(
                    url=message.guild.icon_url)
                await message.author.send(embed=embed)

            else:
                await message.channel.send(embed=discord.Embed("당신은 서버 소유주가 아닙니다."))
        else:
            await message.channel.send(embed=discord.Embed(title="라이센스가 등록되지 않은 서버입니다.\n에서 라이센스를 발급해주세요."))


client.run(tokens)
