import requests
from bs4 import BeautifulSoup
import os

# Removes all characters that can not be in a file path
def clean(toClean):
    cleaned = toClean.replace(':', '')
    cleaned = cleaned.replace('/', '')
    cleaned = cleaned.replace('\\', '')
    cleaned = cleaned.replace('?', '')
    cleaned = cleaned.replace('<brk>', '')
    cleaned = ' '.join(cleaned.split())
    return cleaned


# Asks the user what file location they would like to save the files in
# Folder must be on the same drive as the script being run
print('')
print('Enter the file path you would like to save your files in ')
saveLocation = input();
saveLocation = saveLocation.replace('C:', '')
saveLocation = saveLocation.replace('\\', '/')

# Asks the user for a link to a search query
print('')
print('Enter your search link here ')
currentPage = 'https://dl.acm.org/action/doSearch?SeriesKey=tos&sortBy=downloaded'

# Loops through search pages until it completes all pages
while True:
    searchPage = requests.get(currentPage).text
    searchPage = BeautifulSoup(searchPage, 'html.parser')

    for searchResult in searchPage.find_all('li', attrs={'class': 'search__item'}):
            title = searchResult.find('span', attrs={'class': 'hlFld-Title'}).text.strip()
            title = clean(title)
            
            author = searchResult.find('ul', attrs={'aria-label': 'authors'}).text.strip()
            author = ' '.join(author.split())
            
            issueDetails = searchResult.find('span', attrs={'class': 'epub-section__title'}).text.split(',')
            
            articleDetails = searchResult.find('span', attrs={'class': 'dot-separator'}).text.strip()
            articleDetails = clean(articleDetails)
            
            doi = searchResult.find('a', attrs={'class': 'issue-item__doi'}).text.split('/')
            doi = doi[3] + '-' + doi[4]
            
            attachment = searchResult.find('i', attrs={'class': 'icon-attach_file'})
            
            # Creates the folder structure and save location for downloads
            pdf = 'https://dl.acm.org' + searchResult.find('a', attrs={'data-title': 'PDF'})['href']
            savepath = saveLocation + '/' + issueDetails[0].strip() + '/' + issueDetails[1].strip() + '/' + issueDetails[2].strip() + '/' + articleDetails + '/'
            
            if not os.path.exists(savepath):
                os.makedirs(savepath)
                
            fileSaveLocation = savepath + title + ', DOI ' + doi + '.pdf'

            # Downloads the article if it is not present in the folder
            try:
                with open(fileSaveLocation) as f:
                    print(title, 'has already been downloaded')
                    f.close()
            except FileNotFoundError:
                r2 = requests.get(pdf)
                with open(fileSaveLocation, 'wb') as f:
                    f.write(r2.content)
                    f.close()
                print('Successfully downloaded', title)
            
            
            # Checks if the article has any supplemental material and downloads it
            if attachment is not None:
                downloadPage = 'https://dl.acm.org' + searchResult.find('span', attrs={'class': 'hlFld-Title'}).find('a')['href']
                articlePage = requests.get(downloadPage).text
                articlePage = BeautifulSoup(articlePage, 'html.parser')
                
                for searchResult in articlePage.find_all('div', attrs={'class': 'issue-downloads__item__details'}):
                    supplement = searchResult.find('a')['href']
                    supplementTitle = articlePage.find('span', attrs={'class': 'supplFile--label'}).text
                    if supplementTitle == '':
                        supplementTitle = 'SupplementalMaterial'
                    filetype = supplement.split('.')[-1].split('&')[0]
                    
                    supplementSaveLocation = savepath + supplementTitle + '.' + filetype
                    try:
                        with open(supplementSaveLocation) as f:
                            print(supplementTitle, 'has already been downloaded')
                            f.close()
                    except FileNotFoundError:
                        r2 = requests.get(supplement)
                        with open(supplementSaveLocation, 'wb') as f:
                            f.write(r2.content)
                            f.close()
                        print('Successfully downloaded', supplementTitle)
    
    # Looks for the next page of search results
    nextPage = searchPage.find('a', attrs={'class': 'pagination__btn--next'})
    if nextPage is not None:
        currentPage = nextPage['href']
        print('Finished a search page')
    else:
        break
print('Finished downloading all articles in the search')
exit