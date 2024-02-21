
import requests
import logging
import math
import re
from datetime import datetime
from src.models.Round import Round
from bs4 import BeautifulSoup

def calculateRating(round_list):
    length = len(round_list)
    print("Round Rating List count : " + str(length))
    
    rating_total = 0
    rating_count = 0
    
    for i, rating in enumerate(round_list):
        if rating.included == 'Yes':
            print(str(i) + ', ' + str(rating.roundRating))
            rating_total = int(rating_total) + int(float(rating.roundRating))
            rating_count += 1
    
    print(rating_total)
    topQuarterNum = math.ceil(rating_count * 0.25)
    print(topQuarterNum)
    recent_rounds = round_list[-topQuarterNum:]
    # print(recent_rounds)
    # for rating in recent_rounds:
    #     if rating.included == 'Yes':
    #         print(rating.roundRating)
    #         rating_total = rating_total + int(float(rating.roundRating))
    #         rating_count +=1
    
    # print(rating_count)
    final_rating = math.ceil(rating_total / rating_count)
    # print(final_rating)
    return final_rating

def getUnratedRounds(unratedUrl, round_list, pdga_number, current_rating):
    
    response = requests.get(unratedUrl)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    tmp = soup.find('small', class_='rating-date')
    last_updated_dt = tmp.text.strip()
    last_updated_dt = datetime.strptime((last_updated_dt.replace('(as of ', '').replace(')','')), '%d-%b-%Y')
    
    # print(last_updated_dt)
    table = soup.find('table', id = 'player-results-mpo')

    print('List of Unrated rounds being factored in:')
    for row in table.find_all('tr'):
        
        # Is this tourney after the most recent update? 
        row_date_data = row.find('td', class_='dates')
        if row_date_data is None:
            continue
        row_date = row_date_data.text.strip()
        if 'to' in row_date:
            row_date = row_date.split('to')[1].strip()
               
        # print(row_date)
        tourney_date = datetime.strptime(row_date, '%d-%b-%Y')
        # print(tourney_date)
        
        if tourney_date < last_updated_dt:
            continue
        
        testUrl = ''
        
        for cell in row.find_all('td'):
            if cell['class'][0] == 'tournament':
                refPath = cell.find('a')
                # print(refPath['href'])
                testUrl = 'https://www.pdga.com' + refPath['href']
                # print(cell.text.strip())
                tourneyName = cell.text.strip()
                
        if testUrl != '':
            response1 = requests.get(testUrl)
            
            soup1 = BeautifulSoup(response1.text, "html.parser")
            tournTable = soup1.find('table', id='tournament-stats-0')
            
            for row in tournTable.find_all('tr'):
                
                rowPdgaNum = row.find('td', class_='pdga-number')
                if rowPdgaNum is None:
                    continue
                
                elif rowPdgaNum.text.strip() == pdga_number:
                    
                    for item in row.find_all('td', class_='round-rating'):
                        newRound = Round()
                        newRound.tourneyName = tourneyName
                        newRound.roundRating = item.text.strip()
                        
                        if int(newRound.roundRating) >= current_rating-100:
                            newRound.included = 'Yes'
                        else:
                            newRound.included = 'No'
                        newRound.evaluated = 'No'
                        
                        print(newRound.tourneyName + ', ' + str(newRound.roundRating))
                        round_list.append(newRound)
    
    
def getRatedRounds(ratedUrl, round_list):
    
    # Send a GET request to the website and get the HTML response
    response = requests.get(ratedUrl)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    
    for row in table.find_all('tr'):
        newRound = Round()
    
        for cell in row.find_all('td'):
            
            match cell['class'][0]:
                
                case "tournament":
                    newRound.tourneyName = cell.text.strip()
                    
                case "score":
                    newRound.score = cell.text.strip()
                    
                case "round-rating":
                    newRound.roundRating = int(cell.text.strip())
                
                case "included":
                    newRound.included = cell.text.strip()
                
                case "evaluated":
                    newRound.evaluated = cell.text.strip()
       
        round_list.append(newRound)   
    
## Main function  
def main(pdga_number):
    #Sets up the logger
    # logging.basicConfig(
    #     level=logging.DEBUG,  # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    #     format="%(asctime)s - %(levelname)s - %(message)s",  # Customize the log message format
    #     datefmt="%Y-%m-%d %H:%M:%S",  # Specify the date and time format
    # )
    

    # sets up the urls using that pdga number
    unratedUrl = f"https://www.pdga.com/player/{pdga_number}"
    # logging.info("Player Profile Url: " + unratedUrl)
    ratedUrl = f"https://www.pdga.com/player/{pdga_number}/details"
    # logging.info("Player rating history details url: " + ratedUrl)
    
    round_list = []
    
    getRatedRounds(ratedUrl, round_list) 
    int_rating = calculateRating(round_list)
    print("Current Rating: " + str(int_rating))
    
    getUnratedRounds(unratedUrl, round_list, pdga_number, 924)
    
    # for items in round_list:
    #     print(str(items.roundRating))
    final_rating = calculateRating(round_list)
    print("Calculated Rating: " + str(final_rating))
    
    return [int_rating, final_rating]
    
    
    
if __name__ == "__main__":
    main()