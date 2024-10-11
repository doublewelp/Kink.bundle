# Kink.com Plex Agent

This is an updated version of Vofik's Kink.com Plex Agent [https://github.com/vofik/Kink.bundle]. Most of it needed a rewrite because Kink.com changed their frontend massively and added Cloudflare protection.

# Features

The agent will scrape all Kink.com websites that use the kink.com/shoot/_shoot_id_ URL. Notably, this excludes KinkVR. Will consider support if anyone wants it/asks for it very nicely.

| Data field  | Comment |
| ------------- | ------------- |
| Sitename  | The sitename will be set as the studio (Whippedass, Wiredpussy, etc). |
| Tags  | Shoot tags will be created as Plex collections |
| Title  | Shoot title will be used as the Plex movie title |
| Release Date  | Release date and Year metadata Plex fields will be used |
| Poster  | Trailer preview shot will be used as the Plex movie poster |
| Backgrounds  | Shoot pictures will be used as Plex backgrounds (even if Plex doesn't seem to do much with these...) |
| Summary  | Shoot summary will be added as Plex movie summary |
| Director  | Shoot director will be added as metadata |
| Starring  | All shoot participants will be added as metadata |
| Rating  | Kink shoot rating will be extracted and converted to a 0-100 value for Plex rating |

# Requirements

 - You **MUST** be running Plex on some flavor of Linux where you can run wget and pipe output to stdout. Plex ships with a Python 2.7 environment that runs all agents, and their scraping APIs are all detected by Cloudflare as bots regardless of any headers you send. Instead of using the Plex provided HTML/JSON scrapers, the Agent builds a wget string with enough headers for Kink.com to accept the request.
 - Your Kink.com files need the shoot ID somewhere in the filename. Ideally at the start, but if the search fails, the Agent will attempt to search the rest of the filename for any numbers with 3 or more digits, which are hopefully the shoot number. It broke? Add the shoot number to the start bucko.

# Installation

Get the the bundle folder, stick it in your Plex plugin folder [https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-]. Remember to rename the Kink.bundle-main folder to Kink.bundle. 

Restart Plex if you don't see the new agent. You must use a Movie type library for it to appear.

# FAQ

**Why did you write this? The Plex team said they're going to transition from the old Python agent framework to _something new_.**

This took about 8 hours to write and got me to learn new things (and also to hate the Plex team, thanks for killing the agent documentation page, it was a treat to learn Python syntax from a decade ago and to figure out undocumented APIs by looking at other agents).

**Is this secure?**

About as secure as ancient unsupported Python 2.7 HTML/JSON parsers that download and parse unknown content from the Internet (thanks Plex team, love you almost as much as I love tied up big titty bitches!!).

**Most of this runs fine on my collection but some shoots just don't get any metadata. What gives?**

Kink.com has memory-holed multiple shoots over the years - participant suicide, contracts ran out, lawsuits, more extreme content that just didn't mesh with their current whitewashed sex-positive image. Try to access kink.com/shoot/_shoot_id_ and see what happens. If you get redirected to the list, that shoot is gone from their frontend and all the metadata is lost. Like tears in rain...

**Shit broke! Where's my big titty bondage poster/metadata that I'll never look at?**

Big possibility of breakage. Kink.com doesn't make scraping easy with their nu-Bootstrap style shoot pages and most page elements have practically zero identifying classes/ids. You can't access several elements without brittle XPath expressions that will break the moment their UI/UX guy decides to add a new div (Kink.com UI/UX guy, DO NOT add more divs to that page, I'm begging you sexily).

They're also a porn website with decades of accumulated IT experience and are probably hardened against spammers and scraping. I have no idea if they IP block, but if stuff stops working when you decide to run this against your entire Kink.com 8TB folder well, hopefully you can rub two braincells together and figure out the cause.

**tHIs cODe iSN'T PyTHoNIc!**

Get the fuck out of my house.

# Acknowledgements
 - Vofik for making the original Agent and spiritually pushing me to make this.
 - Fribb for answering a quick question on Reddit. Check out the MAL agent [https://github.com/Fribb/MyAnimeList.bundle] if you're an anime dweeb like me!
 - The Plex team for giving me a whole dose of kicks to the groin. Anything you come up with to replace the agent framework will be better than the current dogshit.
