import discord
from discord.ext import commands
from discord.ext.commands import Bot, has_permissions

from voting import voteDB
from react_decorators import *
from voting.symbols import symbols
from voting.parsers import *
from discord.ext import tasks

# Main poll class, mainly a wrapper around Vote
from voting.vote_manager import VoteManager

import csv

# Built-in Checks for the commands extension of discord py 
# https://gist.github.com/Painezor/eb2519022cd2c907b56624105f94b190

class Voting(commands.Cog):
    bot: Bot

    def __init__(self, bot):
        self.bot = bot
        self.vm = VoteManager(bot)

## Timer für zeitgesteuertes beenden
#        self.timer_check_close.start()

#timer
#    @tasks.loop(seconds=5.0)
#    async def timer_check_close(self):
#        print('ping')
        #print(voteDB.getNextCloseVote())

#wait until bot is ready
#    @timer_check_close.before_loop
#    async def before_printer(self):
#        print('waiting...')
#        await self.bot.wait_until_ready()

    @commands.command(name="createpoll", aliases=["poll", "secretpoll"], help=poll_parser.format_help())
    @commands.guild_only()
    @commands.has_any_role(918443687736934440, 918480805561503764, 902459712778420255) 
    @wait_react
    async def create_poll(self, ctx: Context, *options):
        try:
            print("Parsing args")

            def extra_checks(args):  # Extra checks past the parser's basic ones. These are caught and forwarded in run_parser
                if len(args.options) < 2 or len(symbols) < len(args.options): raise argparse.ArgumentError(opt_arg, f"Between 2 and {len(symbols)} options must be supplied.")
                if args.winners <= 0: raise argparse.ArgumentError(win_arg, f"Cannot select less than 1 winner.")
                if args.limit < 0: raise argparse.ArgumentError(lim_arg, f"Cannot have limit less than 1.")
                for op in args.options:
                    if len(op) > 50: raise argparse.ArgumentError(opt_arg, f"Option {op} is too long. Lines can be no longer than 50 characters (current length {len(op)}))")

            args = run_parser(poll_parser, options, extra_checks)
            # Send feedback or run vote
            if isinstance(args, str): await ctx.send(args)
            else:
                await self.vm.std_vote(ctx, args)

        # Catch any exception, to ensure the bot continues running for other votes
        # and to give error message due to error messages in async blocks not being reported otherwise
        except Exception as e:
            print(e)
            raise e


    @commands.command(name="visiblepoll", aliases=["vpoll"], help=("Runs a poll with visible votes.\n" + vis_poll_parser.format_help()))
    @commands.guild_only()
    @commands.has_any_role(918443687736934440, 918480805561503764, 902459712778420255) 
    @wait_react
    async def create_visible_poll(self, ctx: Context, *options):
        try:
            print("Parsing args")

            def extra_checks(args):  # Extra checks past the parser's basic ones. These are caught and forwarded in run_parser
                if len(args.options) < 2 or len(symbols) < len(args.options): raise argparse.ArgumentError(opt_arg, f"Between 2 and {len(symbols)} options must be supplied.")
                if args.winners <= 0: raise argparse.ArgumentError(win_arg, f"Cannot select less than 1 winner.")
                if args.limit < 0: raise argparse.ArgumentError(lim_arg, f"Cannot have limit less than 1.")
                for op in args.options:
                    if len(op) > 50: raise argparse.ArgumentError(opt_arg, f"Option {op} is too long. Lines can be no longer than 50 characters (current length {len(op)}))")

            args = run_parser(vis_poll_parser, options, extra_checks)
            # Send feedback or run vote
            if isinstance(args, str):
                await ctx.send(args)
            else:
                await self.vm.visible_poll(ctx, args)

        # Catch any exception, to ensure the bot continues running for other votes
        # and to give error message due to error messages in async blocks not being reported otherwise
        except Exception as e:
            print(e)
            raise e



    @commands.command(name="stvpoll", help=("Runs a STV poll.\n" + stv_parser.format_help()))
    @commands.guild_only()
    @commands.has_any_role(918443687736934440, 918480805561503764, 902459712778420255) 
    @wait_react
    async def create_stv_poll(self, ctx: Context, *options):
        try:
            print("Parsing args")

            def extra_checks(args):
                if len(args.options) < 2 or len(symbols) < len(args.options): raise argparse.ArgumentError(opt_arg, f"Between 2 and {len(symbols)} options must be supplied.")
                if args.winners <= 0: raise argparse.ArgumentError(win_arg, f"Cannot select less than 1 winner.")
                if args.limit < 0: raise argparse.ArgumentError(lim_arg, f"Cannot have limit less than 1.")
                for op in args.options:
                    if len(op) > 50: raise argparse.ArgumentError(opt_arg, f"Option {op} is too long. Lines can be no longer than 50 characters (current length {len(op)}))")

            args = run_parser(stv_parser, options, extra_checks)
            if isinstance(args, str): await ctx.send(args)
            else:
                await self.vm.stv_vote(ctx, args)

        except Exception as e:
            print(e)
            raise e

    @has_permissions(administrator=True)
    @commands.command(name="roles", help="Reaction roles")
    @commands.guild_only()
    @wait_react
    async def reaction_roles(self, ctx: Context, *options):
        try:
            print("Parsing args")

            def extra_checks(args):  # Extra checks past the parser's basic ones. These are caught and forwarded in run_parser
                if len(args.options) < 1 or len(symbols) < len(args.options): raise argparse.ArgumentError(opt_arg, f"Between 1 and {len(symbols)} roles must be supplied.")
                if args.limit < 0: raise argparse.ArgumentError(lim_arg, f"Cannot have limit less than 1.")
                for op in args.options:
                    if len(op) > 50: raise argparse.ArgumentError(opt_arg, f"Role name {op} is too long. Lines can be no longer than 50 characters (current length {len(op)}))")

                # TODO CHECK ALL ROLES EXIST

            args = run_parser(poll_parser, options, extra_checks)
            # Send feedback or run vote
            if isinstance(args, str):
                await ctx.send(args)
            else:
                await self.vm.reaction_roles(ctx, args)

        # Catch any exception, to ensure the bot continues running for other votes
        # and to give error message due to error messages in async blocks not being reported otherwise
        except Exception as e:
            print(e)
            raise e


    @commands.command(name="close", aliases=["closepoll", "closevote"], help="Ends a poll with ID `pid`")
    @commands.guild_only()
    @commands.has_any_role(918443687736934440, 918480805561503764, 902459712778420255) 
    @done_react
    @wait_react
    async def close_poll(self, ctx: Context, vid: int):
        #if voteDB.allowedEnd(vid, ctx.author.id):
            await self.vm.close(vid)
        #else: await ctx.send("You cannot end this poll")


    @commands.command(name="voters", help="Gets the number of people who have voted in a poll.")
    @commands.guild_only()
    @wait_react
    async def voters(self, ctx: Context, vid: int):
        #if voteDB.allowedEnd(vid, ctx.author.id):
            voters = voteDB.getVoterCount(vid)
            await ctx.send(f"{voters} people have voted so far in vote {vid}.")
        #else: await ctx.send("Sorry, not allowed!")

    @commands.command(name="showvoters", help="Gets the discord ids + names of people who have voted in a poll.")
    @commands.guild_only()
    @commands.has_any_role(918443687736934440, 918480805561503764, 902459712778420255) 
    @wait_react
    async def showVoters(self, ctx: Context, vid: int):
        #if voteDB.allowedEnd(vid, ctx.author.id):
            members = {'id': 'name'}
            voters = voteDB.getVoterIDs(vid)
            for voter in voters:
                member = ctx.message.guild.get_member(voter[0])
                if member is None:
                    members[voter[0]] = 'unknown'
                else:
                    members[member.id] = member.name + '#' + member.discriminator
            with open('./data/temp/voters.csv', 'w') as f:  
                w = csv.writer(f)
                w.writerows(members.items())
            file = discord.File("./data/temp/voters.csv")
            await ctx.send(file=file, content = f"Ser, here are voters for vote {vid}.")
        #else: await ctx.send("Sorry, only the vote creator can do that!")

    @commands.command(name="myvotes", help="Will DM with your current votes for vote `vid`.")
    @wait_react
    @done_react
    async def myvotes(self, ctx: Context, vid: int):
        user = ctx.author
        await user.create_dm()

        options = [x[1] for x in voteDB.getOptions(vid)]
        uvs = voteDB.getUserVotes(vid, user.id)

        if not uvs: await user.dm_channel.send(f"Poll {vid}: You have no votes so far.")
        else: await user.dm_channel.send(
                f"Poll {vid}: Your current votes are:\n\t\t" +
                '\n\t\t'.join(f"{symbols[i]} **{options[i]}**" for i, _ in uvs)
            )



    @commands.command(name="halt", help="Ends a vote early with no results page.")
    @commands.guild_only()
    @commands.has_any_role(918443687736934440, 918480805561503764, 902459712778420255) 
    @wait_react
    @done_react
    async def halt(self, ctx: Context, vid: int):
        #if voteDB.allowedEnd(vid, ctx.author.id):
            await self.vm.halt(vid)


    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        # user = self.bot.get_user(reaction.user_id)
        user = reaction.member
        emoji = str(reaction.emoji)

        guild: discord.Guild = self.bot.get_guild(reaction.guild_id)
        if not guild: return  # In DM, ignore
        channel: discord.TextChannel = guild.get_channel(reaction.channel_id)
        message: discord.Message = await channel.fetch_message(reaction.message_id)

        if user.bot: return
        await self.vm.on_reaction_add(reaction, emoji, message, user)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent):
        # user = self.bot.get_user(reaction.user_id)
        # user = reaction.member
        emoji = str(reaction.emoji)

        guild: discord.Guild = self.bot.get_guild(reaction.guild_id)
        user = guild.get_member(reaction.user_id)
        if not guild: return  # In DM, ignore
        channel: discord.TextChannel = guild.get_channel(reaction.channel_id)
        message: discord.Message = await channel.fetch_message(reaction.message_id)

        if user.bot: return
        await self.vm.on_reaction_remove(reaction, emoji, message, user)


# Register module with bot
def setup(bot):
    bot.add_cog(Voting(bot))

