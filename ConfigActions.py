import JSON_controls as JC


# Change config value
async def change_config(num, val, ServerInfo):
    try:
        num = int(num)
    except:
        raise ValueError("Not a valid number!")
    if num == 1:
        if val == "wipe":
            Value = {"Server": ServerInfo[0]['Server'], "AllowedChannels": [],
                     "AllowGifs": ServerInfo[0]['AllowGifs']}
            await JC.pop_dict_in_list("Servers.json", ServerInfo[0])
            await JC.write_to_file("Servers.json", Value)
            return
        print(ServerInfo[0])
        await JC.pop_dict_in_list("Servers.json", ServerInfo[0])
        currentChannels = ServerInfo[0]['AllowedChannels']
        currentChannels.append(str(val))
        Value = {"Server": ServerInfo[0]['Server'], "AllowedChannels": currentChannels,
                 "AllowGifs": ServerInfo[0]['AllowGifs']}
        await JC.write_to_file("Servers.json", Value)
    elif num == 2:
        print(ServerInfo[0])
        Value = {"Server": ServerInfo[0]['Server'], "AllowedChannels": ServerInfo[0]['AllowedChannels'],
                 "AllowGifs": val}
        await JC.pop_dict_in_list("Servers.json", ServerInfo[0])
        await JC.write_to_file("Servers.json", Value)


# Check If Channel Is allowed
async def ChannelAllowed(ctx):
    if not ctx.guild:
        return True
    if not await JC.look_for_value_in_file("Servers.json", "Server", str(ctx.guild.id)):
        return True
    ServerInfo = await JC.look_for_value_in_file("Servers.json", "Server", str(ctx.guild.id))
    print(ctx.channel.mention)
    print(ServerInfo[0]['AllowedChannels'])
    if not ServerInfo[0]['AllowedChannels']:
        return True
    for i in ServerInfo[0]['AllowedChannels']:
        if i == ctx.channel.mention:
            return True
    else:
        return False