# RPA_Challenge_-Otomatika

## Description
# Extracting data from a news site
# write the final extrations to /output

### The Source

You are free to choose from any general news website, feel free to select from one of the following examples.

- https://apnews.com/
- https://www.aljazeera.com/
- https://www.reuters.com/
- https://gothamist.com/
- https://www.latimes.com/
- https://news.yahoo.com/

The process must process three parameters via the robocluod work item
  - search phrase
  - news category/section/topic
  - number of months for which you need to receive news (if applicable)
    
    >   Example of how this should work: 0 or 1 - only the current month, 2 - current and previous month, 3 - current and two previous months, and so on
    > 

These may be defined within a configuration file, but we’d prefer they be provided via a [Robocloud workitem](https://rpaframework.org/libraries/robocorp_workitems/)

