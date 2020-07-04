import discord
from discord.ext import commands
import random
import mysql.connector
import json
from threading import Timer
import pandas as pd
import asyncio
import numpy as np

client = commands.Bot(command_prefix='$', help_command=None)

mydb = mysql.connector.connect(
    auth_plugin='mysql_native_password',
    host = 'local',
    user = "##",
    passwd = "##",
    database= "userlevels")

@client.event
async def on_ready():
    print('Bot is ready.')

my_file = open("cash.json", "w")
my_file.write('')
my_file.close()

def save_cash(cash):
    with open("cash.json", "w+") as fp:
        json.dump(cash, fp, indent=4)

def clear():
    my_file = open("cash.json", "w+")
    for x in my_file:
        del x

    my_file.close()

def generateXP():
    return random.randint(1, 100)

def levelsystem(xp):
    for num in range(100):
      yield num ** 4

array = []
for x in levelsystem(100):
  array.append(x)

def pointLevel(points):
    for index, xp in enumerate(array):
        if points < xp:
            level = index
            return level

def jackpotaction():

    with open("cash.json") as fp:
        cash = json.load(fp)

    retirar = []
    valores = []
    participantes = []
    nomes = []
    total = 0
    for x in cash:
        individuo = cash[x].split(',')

        apostado = ([int(individuo[1]), int(individuo[2])])
        retirar.append(apostado)

        nome = str(individuo[0])
        nomes.append(nome)

        participante = str(individuo[1])
        participantes.append(participante)

        valor = int(individuo[2])

        total = total + int(valor)

        cursor = mydb.cursor()
        cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(participante))

        result = cursor.fetchall()

        newXP = result[0][0] - valor
        cursor.execute("UPDATE users SET user_xp = " + str(newXP) + " WHERE client_id = " + str(participante))

        mydb.commit()


    valores = []
    for i in cash:
        individuo = cash[i].split(',')
        porcentagem = (int(individuo[2])/total)
        valores.append(porcentagem)

    vencedor = roleta(participantes, valores, nomes)

    my_venc = open('vencedor.txt', 'w')
    num = nomes.index(vencedor[0])
    id = participantes[num]
    valores = valores[num]*100

    my_venc.write(f'{vencedor[0]} com {valores}%')
    my_venc.close()

    cursor = mydb.cursor()
    cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(id))

    result = cursor.fetchall()

    newXP = result[0][0] + total

    cursor.execute("UPDATE users SET user_xp = " + str(newXP) + " WHERE client_id = " + str(id))
    mydb.commit()

    print(vencedor[0], id, num, valores)

    clear()

def roleta(participantes, valores, nomes):
    vencedor = np.random.choice(nomes, 1, p=valores)
    return(vencedor)

def porcentagem():

    with open("cash.json", 'r') as fp:
        cash = json.load(fp)


    total = 0

    bet = cash
    for i in bet:
        individuo = bet[i].split(',')
        total = total + int(individuo[2])


    lista = []
    for i in bet:
        individuo = bet[i].split(',')
        porcentagem = (int(individuo[2])/total)*100
        lista.append(f'{individuo[0]} tem {"{0:.2f}".format(round(porcentagem,2))}% do pot')

    return(lista)

@client.command()
async def roubar(message, arg, arg1):
    valor = int(arg)
    arg1 = arg1.replace('<','')
    arg1 = arg1.replace('>','')
    arg1 = arg1.replace('@','')
    alvoid = arg1.replace('!','')

    moeda = np.random.choice(['cara','coroa'],1, p=[0.3,0.7])

    cursor = mydb.cursor()
    cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(message.author.id))
    result = cursor.fetchall()
    seuXP = int(result[0][0])

    cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(alvoid))
    result = cursor.fetchall()
    alvoXP = int(result[0][0])

    if seuXP > valor and alvoXP >= valor:
        await message.channel.send(f'Roubando você tem 30% de chance de ganhar.')

        if str(moeda[0]) == 'cara':

            seufinal = seuXP+valor
            cursor.execute("UPDATE users SET user_xp = " + str(seufinal) + " WHERE client_id = " + str(message.author.id))
            alvofinal = alvoXP-valor
            cursor.execute("UPDATE users SET user_xp = " + str(alvofinal) + " WHERE client_id = " + str(alvoid))
            mydb.commit()

            await message.channel.send(f'Você roubou com sucesso {valor} de <@{alvoid}>')

        if str(moeda[0]) == 'coroa':

            seufinal = seuXP-valor
            cursor.execute("UPDATE users SET user_xp = " + str(seufinal) + " WHERE client_id = " + str(message.author.id))
            alvofinal = alvoXP+valor
            cursor.execute("UPDATE users SET user_xp = " + str(alvofinal) + " WHERE client_id = " + str(alvoid))
            mydb.commit()

            await message.channel.send(f'Você não conseguiu roubar e entregou {valor} para <@{alvoid}>')
    else:
            await message.channel.send(f'OPERAÇÃO ILEGAL!')

@client.command()
@commands.cooldown(1, 32, commands.BucketType.guild)
async def jackpot(message):

    clear()
    timer = Timer(31, jackpotaction)
    timer.start()
    await message.channel.send('Roleta em 30 segundos!')

    counter = 0

    while counter<8:
        if counter == 3:
            lista = porcentagem()
            lista = '\n'.join(map(str, lista))
            embed = discord.Embed(
                title = f'Faltam 15 segundos! Condições: \n{lista}')
            await message.channel.send(embed = embed)

        if counter == 6:
            lista = porcentagem()
            lista = '\n'.join(map(str, lista))
            embed = discord.Embed(
                title = f'As bets fecharam! Rodando na sorte! Condições: \n{lista}'
            )
            await message.channel.send(embed=embed)

        if counter == 7:
            my_venc = open('vencedor.txt', 'r')
            vencedor = my_venc.read()
            embed = discord.Embed(
                title = f'O vencedor é: {vencedor}')

            await message.channel.send(embed=embed)
            my_venc.close()

            my_file = open("vencedor.txt", "w+")
            for x in my_file:
                del x
            my_file.close()
            clear()

        print(counter)
        counter = counter + 1
        await asyncio.sleep(5)

@client.command()
async def double(message, arg):
    arg = int(arg)

    moeda = np.random.choice(['cara','coroa'],1, p=[0.46,0.54])

    cursor = mydb.cursor()
    cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(message.author.id))
    result = cursor.fetchall()
    currentXP = int(result[0][0])

    if arg < currentXP:

        if str(moeda[0]) == 'cara':
            arg = arg*2
            newXP = currentXP + arg
            cursor.execute("UPDATE users SET user_xp = " + str(newXP) + " WHERE client_id = " + str(message.author.id))
            mydb.commit()
            embed = discord.Embed(
                title = f'{message.author.name} dobrou o valor de {arg/2} para {arg}!'
            )

            await message.channel.send(embed=embed)

        if str(moeda[0]) == 'coroa':
            newXP = currentXP - arg
            cursor.execute("UPDATE users SET user_xp = " + str(newXP) + " WHERE client_id = " + str(message.author.id))
            mydb.commit()

            embed = discord.Embed(
                title = f'{message.author.name} perdeu {arg}.'
            )

            await message.channel.send(embed = embed)

    else:
        await message.channel.send(f'Operação ilegal.')

@client.command()
async def rank(message):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users")

    df = pd.DataFrame(cursor.fetchall())

    df = df.sort_values(by=[1], ascending=False, ignore_index=True)

    rank = getIndexes(df, message.author.id)
    rank = int(rank[0][0] + 1)
    print(rank, type(rank))

    if rank == 1:
        file = discord.File("emojis/JIMENEZ.jpg", filename="JIMENEZ.jpg")
        embed = discord.Embed(
            title = 'O Pai',
            description = 'Você não é só o mais rico do clã como também é o melhor apostador',
        )
        embed.set_image(url="attachment://JIMENEZ.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)

    if rank == 2:
        file = discord.File("emojis/CRUZ.jpg", filename="CRUZ.jpg")
        embed = discord.Embed(
            title = 'O quase pai',
            description = 'Você é quase húngaro, a realeza te aguarda. Não está em primeiro mas é tão chave quanto.',
        )
        embed.set_image(url="attachment://CRUZ.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)

    if rank == 3:
        file = discord.File("emojis/MATHEUS.jpg", filename="MATHEUS.jpg")
        embed = discord.Embed(
            title = 'O pasteleiro',
            description = 'Sua posição é tão elegante quanto meus pezinhos, não é nem primeiro nem segundo mas vale a pena.',
        )
        embed.set_image(url="attachment://CRUZ.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)

    if rank == 4:
        file = discord.File("emojis/TATA.jpg", filename="TATA.jpg")
        embed = discord.Embed(
            title = 'O chavoso',
            description = 'Você não tão bom mas é digno de usar o bonézinho rosa.',
        )
        embed.set_image(url="attachment://TATA.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)

    if rank == 5:
        file = discord.File("emojis/SCHWARZ.jpg", filename="SCHWARZ.jpg")
        embed = discord.Embed(
            title = 'O bolante',
            description = 'Você manda bem mas queimou largada e tomou.',
        )
        embed.set_image(url="attachment://SCHWARZ.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)

    if rank == 6:
        file = discord.File("emojis/DANILO.jpg", filename="DANILO.jpg")
        embed = discord.Embed(
            title = 'O comunista',
            description = 'Tá com muito dinheiro pra um comunista',
        )
        embed.set_image(url="attachment://DANILO.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)

    if rank > 6:
        file = discord.File("emojis/JULIO.jpg", filename="JULIO.jpg")
        embed = discord.Embed(
            title = 'O cornão da quebrada',
            description = 'No mínimo prego',
        )
        embed.set_image(url="attachment://JULIO.jpg")
        embed.set_author(name=f'Você está no rank #{rank}')

        await message.channel.send(file=file, embed=embed)
        #
        #
        # id = f'<@{message.author.id}>'
        # await message.channel.send(f'{id} está no rank #{rank}')

@client.command()
async def rankall(message):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users")

    df = pd.DataFrame(cursor.fetchall())
    df = df.sort_values(by=[1], ascending=False, ignore_index=True)

    for x, value in enumerate(df[0]):
        df[0][x] = f'<@{value}>'

    embed = discord.Embed(
        title='Rank dos brabo',
        description = f'{df.to_string(header=False)}'
    )

    await message.channel.send(embed=embed)

@client.command()
async def help(message):
    help = open('help.txt', 'r')
    help = help.read()
    embed = discord.Embed(
        title='BDP SERVER',
        description = help
    )
    await message.channel.send(embed = embed)

@client.command()
async def xp(message):
    cursor = mydb.cursor()
    cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(message.author.id))
    result = cursor.fetchall()
    newXP = result[0][0]
    lvl = pointLevel(int(newXP))
    embed = discord.Embed(title = str(message.author.name) + "\nSeu saldo de BDPoints é: " + str(newXP) + "\nSeu Level é: " + str(lvl))
    await message.channel.send(embed=embed)

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.lower().startswith('bet'):
        arg = message.content.lower()
        arg = arg [4:]

        cursor = mydb.cursor()
        cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(message.author.id))
        result = cursor.fetchall()
        current = int(result[0][0])

        my_file = open("cash.json", "r")
        if my_file.read() == '':
            my_file.close()
            my_file = open("cash.json", "w")
            my_file.write('{}')
            my_file.close()

        with open("cash.json") as fp:
            cash = json.load(fp)

        if current<0:
            discord.Embed(
                title = f'{message.author.name} apostou {arg}'
            )
            await message.channel.send(embed = embed)

        arg = int(arg)
        if arg>current:
            arg = current

            embed = discord.Embed(
                title= f'{message.author.name}, você não tem esse tanto!'
            )
            await message.channel.send(embed=embed)

        if arg<current:
            cash[message.author.name] = f'{message.author.name},{message.author.id},{arg}'
            save_cash(cash)
            embed = discord.Embed(
                title=f'{message.author.name} apostou {arg}'
            )

            await message.channel.send(embed = embed)

    if message.content.lower().startswith('!rank'):
        await message.channel.send('PARA DE DAR IBOPE PRA CONCORRÊNCIA! Teste $help para nossos comandos')

    else:
        xp = generateXP()
        cursor = mydb.cursor()
        cursor.execute("SELECT user_xp FROM users WHERE client_id = " +str(message.author.id))
        result = cursor.fetchall()
        if(len(result) == 0): ##User is not in DB
            print('User is not in db, add him...')
            cursor.execute("INSERT INTO users VALUES(" + str(message.author.id) + "," + str(xp) + ")")
            mydb.commit()
            print('inserted')
        else:
            newXP = result[0][0] + xp
            cursor.execute("UPDATE users SET user_xp = " + str(newXP) + " WHERE client_id = " + str(message.author.id))
            mydb.commit()


    await client.process_commands(message)

    #
    # @client.listen('on_message')
    # async def emoji(message):
    #     if message.content.lower() == "emoji":

def getIndexes(dfObj, value):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos

@client.command()
async def clearmsg(message, number=1000):
    number = int(number)
    await message.channel.purge(limit=number)

client.run("NzI3MzQyMTE3OTMxOTc0NzA2.XvqcSA.fHeLnbx_-5kGrTw5N236_oLOLdE")
