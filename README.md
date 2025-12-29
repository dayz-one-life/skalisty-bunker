# DayZ Chernarus: _Skalisty Bunker_

## Installation

1. Copy skalisty-bunker.json and skalisty-bunker-pra.json to your custom folder.
2. Add the following to your cfggameplay.json object spawner array.
```json
{
  "WorldsData":
  {
    "objectSpawnerArr": [
      "./custom/skalisty-bunker.json" 
    ]
  }
}
```
3. Add the following to your cfggameplay.json playerRestrictedAreaFiles array.
```json
{
  "WorldsData":
  {
    "playerRestrictedAreaFiles": [
      "./custom/skalisty-bunker-pra.json"
    ]
  }
}
```
4. Add the lines in mapgroupproto-entries.txt to your mapgroupproto.xml file.
5. Add the lines in mapgrouppos-entries.txt to your mapgrouppos.xml file.
6. Add the lines in undergroundtrigger-entries.txt to your cfgundergroundtriggers.json file.
7. Optional: Replace your areaflags.map with the one from this repo to make Skalisty island a Tier 4 zone.

## Accessing the Bunker
You will need to provide a way for your players to obtain a punch card to access the main part of the bunker, and a red shipping container key to access the lowest part of the bunker. You can add the following entries to your db/types.xml file to have them spawn in contaminated areas, or you can come up with something more creative.
```xml
    <type name="PunchedCard">
        <nominal>1</nominal>
        <lifetime>1800</lifetime>
        <restock>0</restock>
        <min>1</min>
        <quantmin>100</quantmin>
        <quantmax>100</quantmax>
        <cost>100</cost>
        <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
        <category name="tools"/>
        <usage name="ContaminatedArea"/>
    </type>
    <type name="ShippingContainerKeys_Red">
        <nominal>1</nominal>
        <lifetime>1800</lifetime>
        <restock>0</restock>
        <min>1</min>
        <quantmin>100</quantmin>
        <quantmax>100</quantmax>
        <cost>100</cost>
        <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
        <category name="tools"/>
        <usage name="ContaminatedArea"/>
    </type>
```
It's also recommended to adjust the damage on these items so that they can only be used once. Adjust the settings in cfgspawnabletypes.xml to make these single use.
```xml
    <type name="ShippingContainerKeys_Red">
        <damage min="0.8" max="0.8" />
    </type>
    <type name="PunchedCard">
        <damage min="0.8" max="0.8" />
    </type>
```

## See it in Action
Join the One Life Winter Chernarus server to see the bunker in action!
### [One Life Discord](https://dayzonelife.com)

