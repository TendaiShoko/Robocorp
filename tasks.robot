*** Settings ***
Documentation     A simple RPA task for scraping news from a website.
Library           RPA.Browser.Selenium
Library           RPA.Excel.Files
Library           RPA.Robocorp.WorkItems
Library           DateTime
Resource          keywords.robot

*** Variables ***
${SEARCH_PHRASE}    YOUR_SEARCH_PHRASE
${NEWS_CATEGORY}    YOUR_NEWS_CATEGORY
${NUM_MONTHS}       YOUR_NUM_MONTHS
${OUTPUT_FILE}      ${CURDIR}/output/news_data.xlsx

*** Tasks ***
Scrape News Data
    Open Browser To Al Jazeera
    Search For News
    Process News Articles
    [Teardown]    Close Browser

*** Keywords ***
Open Browser To Al Jazeera
    Open Available Browser    https://www.aljazeera.com/

Search For News
    Input Text    css:#search-input    ${SEARCH_PHRASE}
    Press Keys    css:#search-input    ENTER

Process News Articles
    ${date_range}=    Get Date Range    ${NUM_MONTHS}
    ${news_items}=    Get News Articles    ${date_range}
    Create Workbook    ${OUTPUT_FILE}
    FOR    ${item}    IN    @{news_items}
        ${data}=    Get News Data    ${item}
        Append Row To Worksheet    ${OUTPUT_FILE}    ${data}
    END

Close Browser
    Close All Browsers
