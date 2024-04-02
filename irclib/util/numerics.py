"""IRC numeric mapping"""

from dataclasses import dataclass
from typing import Iterator, Mapping

__all__ = ("Numeric", "numerics")


@dataclass
class Numeric:
    name: str
    numeric: int


class NumericsDict(Mapping[str, Numeric]):
    """Mapping of IRC numerics"""

    def __init__(self, *args: Numeric) -> None:
        super().__init__()
        self.data = args
        self.names = {num.name: num for num in args}
        self.nums = {num.numeric: num for num in args}
        self.num_strs = {str(num.numeric).zfill(3): num for num in args}

    def from_int(self, n: int) -> Numeric:
        """Get a numeric by its number"""
        return self.nums[n]

    def from_name(self, name: str) -> Numeric:
        """Get a numeric by name."""
        return self.names[name.upper()]

    def __iter__(self) -> Iterator[str]:
        return iter(self.num_strs)

    def __len__(self) -> int:
        return len(self.names)

    def __getitem__(self, key: str) -> Numeric:
        return self.nums[int(key)]

    def __getattr__(self, item: str) -> Numeric:
        try:
            return self.names[str(item).upper()]
        except LookupError:
            raise AttributeError(item) from None


numerics = NumericsDict(
    Numeric("RPL_WELCOME", 1),
    Numeric("RPL_YOURHOST", 2),
    Numeric("RPL_CREATED", 3),
    Numeric("RPL_MYINFO", 4),
    Numeric("RPL_BOUNCE", 5),
    Numeric("RPL_TRACELINK", 200),
    Numeric("RPL_TRACECONNECTING", 201),
    Numeric("RPL_TRACEHANDSHAKE", 202),
    Numeric("RPL_TRACEUNKNOWN", 203),
    Numeric("RPL_TRACEOPERATOR", 204),
    Numeric("RPL_TRACEUSER", 205),
    Numeric("RPL_TRACESERVER", 206),
    Numeric("RPL_TRACESERVICE", 207),
    Numeric("RPL_TRACENEWTYPE", 208),
    Numeric("RPL_TRACECLASS", 209),
    Numeric("RPL_TRACERECONNECT", 210),
    Numeric("RPL_STATSLINKINFO", 211),
    Numeric("RPL_STATSCOMMANDS", 212),
    Numeric("RPL_STATSCLINE", 213),
    Numeric("RPL_STATSNLINE", 214),
    Numeric("RPL_STATSILINE", 215),
    Numeric("RPL_STATSKLINE", 216),
    Numeric("RPL_STATSQLINE", 217),
    Numeric("RPL_STATSYLINE", 218),
    Numeric("RPL_ENDOFSTATS", 219),
    Numeric("RPL_UMODEIS", 221),
    Numeric("RPL_SERVICEINFO", 231),
    Numeric("RPL_ENDOFSERVICES", 232),
    Numeric("RPL_SERVICE", 233),
    Numeric("RPL_SERVLIST", 234),
    Numeric("RPL_SERVLISTEND", 235),
    Numeric("RPL_STATSVLINE", 240),
    Numeric("RPL_STATSLLINE", 241),
    Numeric("RPL_STATSUPTIME", 242),
    Numeric("RPL_STATSOLINE", 243),
    Numeric("RPL_STATSHLINE", 244),
    Numeric("RPL_STATSPING", 246),
    Numeric("RPL_STATSBLINE", 247),
    Numeric("RPL_STATSDLINE", 250),
    Numeric("RPL_LUSERCLIENT", 251),
    Numeric("RPL_LUSEROP", 252),
    Numeric("RPL_LUSERUNKNOWN", 253),
    Numeric("RPL_LUSERCHANNELS", 254),
    Numeric("RPL_LUSERME", 255),
    Numeric("RPL_ADMINME", 256),
    Numeric("RPL_ADMINLOC1", 257),
    Numeric("RPL_ADMINLOC2", 258),
    Numeric("RPL_ADMINEMAIL", 259),
    Numeric("RPL_TRACELOG", 261),
    Numeric("RPL_TRACEEND", 262),
    Numeric("RPL_TRYAGAIN", 263),
    Numeric("RPL_NONE", 300),
    Numeric("RPL_AWAY", 301),
    Numeric("RPL_USERHOST", 302),
    Numeric("RPL_ISON", 303),
    Numeric("RPL_UNAWAY", 305),
    Numeric("RPL_NOWAWAY", 306),
    Numeric("RPL_WHOISUSER", 311),
    Numeric("RPL_WHOISSERVER", 312),
    Numeric("RPL_WHOISOPERATOR", 313),
    Numeric("RPL_WHOWASUSER", 314),
    Numeric("RPL_ENDOFWHO", 315),
    Numeric("RPL_WHOISCHANOP", 316),
    Numeric("RPL_WHOISIDLE", 317),
    Numeric("RPL_ENDOFWHOIS", 318),
    Numeric("RPL_WHOISCHANNELS", 319),
    Numeric("RPL_LISTSTART", 321),
    Numeric("RPL_LIST", 322),
    Numeric("RPL_LISTEND", 323),
    Numeric("RPL_CHANNELMODEIS", 324),
    Numeric("RPL_UNIQOPIS", 325),
    Numeric("RPL_NOTOPIC", 331),
    Numeric("RPL_TOPIC", 332),
    Numeric("RPL_INVITING", 341),
    Numeric("RPL_SUMMONING", 342),
    Numeric("RPL_INVITELIST", 346),
    Numeric("RPL_ENDOFINVITELIST", 347),
    Numeric("RPL_EXCEPTLIST", 348),
    Numeric("RPL_ENDOFEXCEPTLIST", 349),
    Numeric("RPL_VERSION", 351),
    Numeric("RPL_WHOREPLY", 352),
    Numeric("RPL_NAMREPLY", 353),
    Numeric("RPL_KILLDONE", 361),
    Numeric("RPL_CLOSING", 362),
    Numeric("RPL_CLOSEEND", 363),
    Numeric("RPL_LINKS", 364),
    Numeric("RPL_ENDOFLINKS", 365),
    Numeric("RPL_ENDOFNAMES", 366),
    Numeric("RPL_BANLIST", 367),
    Numeric("RPL_ENDOFBANLIST", 368),
    Numeric("RPL_ENDOFWHOWAS", 369),
    Numeric("RPL_INFO", 371),
    Numeric("RPL_MOTD", 372),
    Numeric("RPL_INFOSTART", 373),
    Numeric("RPL_ENDOFINFO", 374),
    Numeric("RPL_MOTDSTART", 375),
    Numeric("RPL_ENDOFMOTD", 376),
    Numeric("RPL_YOUREOPER", 381),
    Numeric("RPL_REHASHING", 382),
    Numeric("RPL_YOURESERVICE", 383),
    Numeric("RPL_MYPORTIS", 384),
    Numeric("RPL_TIME", 391),
    Numeric("RPL_USERSSTART", 392),
    Numeric("RPL_USERS", 393),
    Numeric("RPL_ENDOFUSERS", 394),
    Numeric("RPL_NOUSERS", 395),
    Numeric("ERR_NOSUCHNICK", 401),
    Numeric("ERR_NOSUCHSERVER", 402),
    Numeric("ERR_NOSUCHCHANNEL", 403),
    Numeric("ERR_CANNOTSENDTOCHAN", 404),
    Numeric("ERR_TOOMANYCHANNELS", 405),
    Numeric("ERR_WASNOSUCHNICK", 406),
    Numeric("ERR_TOOMANYTARGETS", 407),
    Numeric("ERR_NOSUCHSERVICE", 408),
    Numeric("ERR_NOORIGIN", 409),
    Numeric("ERR_NORECIPIENT", 411),
    Numeric("ERR_NOTEXTTOSEND", 412),
    Numeric("ERR_NOTOPLEVEL", 413),
    Numeric("ERR_WILDTOPLEVEL", 414),
    Numeric("ERR_BADMASK", 415),
    Numeric("ERR_UNKNOWNCOMMAND", 421),
    Numeric("ERR_NOMOTD", 422),
    Numeric("ERR_NOADMININFO", 423),
    Numeric("ERR_FILEERROR", 424),
    Numeric("ERR_NONICKNAMEGIVEN", 431),
    Numeric("ERR_ERRONEUSNICKNAME", 432),
    Numeric("ERR_NICKNAMEINUSE", 433),
    Numeric("ERR_NICKCOLLISION", 436),
    Numeric("ERR_UNAVAILRESOURCE", 437),
    Numeric("ERR_USERNOTINCHANNEL", 441),
    Numeric("ERR_NOTONCHANNEL", 442),
    Numeric("ERR_USERONCHANNEL", 443),
    Numeric("ERR_NOLOGIN", 444),
    Numeric("ERR_SUMMONDISABLED", 445),
    Numeric("ERR_USERSDISABLED", 446),
    Numeric("ERR_NOTREGISTERED", 451),
    Numeric("ERR_NEEDMOREPARAMS", 461),
    Numeric("ERR_ALREADYREGISTERED", 462),
    Numeric("ERR_NOPERMFORHOST", 463),
    Numeric("ERR_PASSWDMISMATCH", 464),
    Numeric("ERR_YOUREBANNEDCREEP", 465),
    Numeric("ERR_YOUWILLBEBANNED", 466),
    Numeric("ERR_KEYSET", 467),
    Numeric("ERR_CHANNELISFULL", 471),
    Numeric("ERR_UNKNOWNMODE", 472),
    Numeric("ERR_INVITEONLYCHAN", 473),
    Numeric("ERR_BANNEDFROMCHAN", 474),
    Numeric("ERR_BADCHANNELKEY", 475),
    Numeric("ERR_BADCHANMASK", 476),
    Numeric("ERR_NOCHANMODES", 477),
    Numeric("ERR_BANLISTFULL", 478),
    Numeric("ERR_NOPRIVILEGES", 481),
    Numeric("ERR_CHANOPRIVSNEEDED", 482),
    Numeric("ERR_CANTKILLSERVER", 483),
    Numeric("ERR_RESTRICTED", 484),
    Numeric("ERR_UNIQOPRIVSNEEDED", 485),
    Numeric("ERR_NOOPERHOST", 491),
    Numeric("ERR_NOSERVICEHOST", 492),
    Numeric("ERR_UMODEUNKNOWNFLAG", 501),
    Numeric("ERR_USERSDONTMATCH", 502),
)
