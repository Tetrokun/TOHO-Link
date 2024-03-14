#Touhou Homage Linker (TOHO-Link)

TOHO-Link is a fan-created tool designed to seamlessly connect Touhou cover songs with their original compositions in your plex instance, leverageing collections.

Use at your own risk, No warenty. 
Use on a test library if you care about your production library
In my case I didn't test, and it improperly matched non touhou songs to collections sometimes. In an ideal scenario this would be more isolated.



Requirements

    Python 3.x
    Plex Media Server with a music library populated from the TLMC
    A copy of the touhou-music.db from https://github.com/solaasan/Touhou-Music-Database    
    plexapi Python library
    colorama Python library for enhanced console output

Installation

    Ensure Python 3.x is installed on your system.
    Clone this repository to your local machine.


git clone https://github.com/yourusername/TOHO-Link.git

Usage

    Edit the py file and put in your information at the bottom, 
    Run the script
    Watch it go, It may take awhilewith large libraries to A: load, and B: map all your songs. 
    ???
    Profit.

To come:
  We will see if I continue to work on this, but it's useful in it's current state. Expect breaking changes to come if this is updated
  It needs better matching functionality, perhaps migrating to the online hosted touhoumusic db.
  Name collections better? right now it just uses the moonrunes, would be better to do something like: Faith is for the Transient People ~ (信仰は儚き人間の為に)
  thread the collection mapping process with concurent futures. 
  
