from cowsay import cowsay, list_cows, read_dot_cow #, cowthink, get_random_cow
import argparse

parser = argparse.ArgumentParser()

parser.add_argument( 	"message", 
			help="what will the cow say", 
			nargs='?', 
			default="", 
			type=str)

parser.add_argument(	"-e", "--eye_string", 
			help="select the appearance of the cow's eyes", 
			default="oo", 
			type=str)

parser.add_argument(	"-f", "--cowfile", 
			help="""contains '/' => path; else => search in the COWPATH""", 
			default="default", 
			type=str)

parser.add_argument(	"-l", "--list", 
			help="list of all cowfiles", 
			action="store_true")

parser.add_argument(	"-n", "--wrap_text", 
			help="wrap_text", 
			action='store_false')

parser.add_argument(	"-T", "--tongue_string", 
			help="select the appearance of the cow's tongue", 
			default="  ", 
			type=str)

parser.add_argument(	"-W", "--column", 
			help="eyes", 
			default=40, 
			type=int)

parser.add_argument("-b", "--borg", 	help="borg", 	 action="store_true")
parser.add_argument("-d", "--dead", 	help="dead", 	 action="store_true")
parser.add_argument("-g", "--greedy", 	help="greedy", 	 action="store_true")
parser.add_argument("-p", "--paranoia", help="paranoia", action="store_true")
parser.add_argument("-s", "--stoned", 	help="stoned",	 action="store_true")
parser.add_argument("-t", "--tired", 	help="tired", 	 action="store_true")
parser.add_argument("-w", "--wakeup", 	help="wakeup", 	 action="store_true")
parser.add_argument("-y", "--youthful", help="youthful", action="store_true")


args = parser.parse_args()

args.eye_string = args.eye_string[:2]
args.tongue_string = args.tongue_string[:2]

if "/" in args.cowfile or args.cowfile[-4:] == ".cow":
	args.cow = "default"
	with open(args.cowfile) as file:
		args.cowfile = read_dot_cow(file)
else:
	args.cow = args.cowfile
	args.cowfile = None
	

d = {	"b": args.borg, 
	"d": args.dead, 
	"g": args.greedy, 
	"p": args.paranoia, 
	"s": args.stoned,
	"t": args.tired,
	"w": args.wakeup,
	"y": args.youthful}

preset = sorted(d.items(), key=lambda x: (x[1], x[0]))
preset = preset[-1]
if preset[1]:
	preset = preset[0]
else:
	preset = None

if args.list:
	print(list_cows())
else:
	print(cowsay(	args.message, cow=args.cow, preset=preset, 
			eyes=args.eye_string, tongue=args.tongue_string, 
			width=args.column, wrap_text=True, cowfile=args.cowfile))
