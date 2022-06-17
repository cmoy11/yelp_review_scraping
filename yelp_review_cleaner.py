import os
import csv
from datetime import datetime
import re
import matplotlib.pyplot as plt
import numpy as np
import datetime as DT
import matplotlib.dates as mdates
import sqlite3
import nltk

def create_visualizations(city):
    # get list of all csv files created by yelp_review_scraper
    directory = f'{city}/review_csvs'
    csv_files = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            csv_files.append(f)

    all_reviews = []
    tdata = {}
    for file in csv_files:
        print(file)
        if file == f'{city}/review_csvs/.DS_Store':
            continue
        with open(file, newline='\n') as csvfile:
            # reads all data from each file generated in yelp_review_scraper.py
            reader = csv.reader(csvfile)
            next(reader)
            data = []
            restaurant_name = file.replace(f'{city}/review_csvs/', '').replace('-', ' ').replace('.csv', '')

            # creates csv reader object and loops through each reveiw for the restaurant
            for row in reader:
                date=row[0]

                regex = r"(\d{1,2})\/\d{1,2}\/\d{4}"
                regex2 = r"\d{1,2}\/(\d{1,2})\/\d{4}"
                regex3 = r"\d{1,2}\/\d{1,2}\/(\d{4})"

                # loops through csv reader and gets date information
                month = re.findall(regex, date)
                day = re.findall(regex2, date)
                year = re.findall(regex3, date)

                # converts dates into sortable format
                if len(month[0]) == 1:
                    month[0] = '0' + month[0]
                if len(day[0]) == 1:
                    day[0] = '0' + day[0]

                new_date = year[0] + month[0] + day[0]

                star = row[1][0]
                review = row[2]

                # creates list for each review
                review_list = [date, int(new_date), int(star), review.replace('¬†', '').replace(' \xa0', ' '), restaurant_name]
                if review_list in data:
                    continue
                
                # appends review list to both local (restaurant only) and global (complete) lists of reviews
                data.append(review_list[:4])
                all_reviews.append(review_list)

            # sorts reviews based on date
            sorted_data = sorted(data, key = lambda x:x[1])
            sum = 0
            count = 0
            averaged_data = []

            # creates running average for reviews
            for row in sorted_data:
                date = row[0]
                converted_date = row[1]
                rating = row[2]
                review = row[3]

                sum += rating
                count += 1

                average = round(sum/count, 2)
                averaged_data.append([date, converted_date, rating, average, review])

            # writes csv file with averaged value for each restaurant
            filename = file.replace(f'{city}/review_csvs', f'{city}/cleaned_csvs')
            with open(filename, "w") as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["date", "converted_date", "rating", "average", "review"])
                for row in averaged_data:
                    date = row[0]
                    converted_date = row[1]
                    rating = row[2]
                    average = row[3]
                    review = row[4]
                    csvwriter.writerow([date, converted_date, rating, average, review])

            # creates data visualization plotting number of reviews and average star rating for each restaurant
            dates = [str(DT.datetime.strptime(str(int(review[1])),'%Y%m%d'))[:10] for review in averaged_data]
            raw_dates = [np.datetime64(d) for d in dates]
            num_reviews = range(1, len(averaged_data) + 1)
            averages = [x[3] for x in averaged_data]
            total_reviews = len(averaged_data)
            final_average = averages[-1]

            fig, ax1 = plt.subplots()

            ax2 = ax1.twinx()
            ax1.plot(raw_dates, num_reviews, 'r-')
            ax2.plot(raw_dates, averages, 'b-')

            xfmt = mdates.DateFormatter('%Y-%m-%d')
            ax1.xaxis.set_major_formatter(xfmt)
            xticks = ['2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01', '2020-05-25', '2021-01-01', '2022-01-01']
            ax1.set_xticks(xticks)
            ax1.set_xticklabels(['2017', '2018', '2019', '2020', 'May 25,\n2020', '2021', '2022'])
            plt.xticks(rotation=25)

            ax1.set_xlabel('Date')
            ax1.set_ylabel('Number of Reviews', color='r')
            ax2.set_ylabel('Average Star Rating', color='b')
            ax1.set_title(restaurant_name)

            plt.axvline(DT.datetime(2020, 3, 15), color='g', linestyle="--", label='begining of Covid-19 Pandemic')
            plt.axvline(DT.datetime(2020, 5, 25), color='k', linestyle="--", label='murder of Gorge Floyd')
            plt.tight_layout()
            plt.show()

            # gets data off of plots
            t0_reviewcount = int(np.interp(np.datetime64('2020-02-15'), raw_dates, num_reviews))
            t0_average = round(np.interp(np.datetime64('2020-02-15'), raw_dates, averages),2)
            t1_reviewcount = int(np.interp(np.datetime64('2020-03-15'), raw_dates, num_reviews))
            t1_average = round(np.interp(np.datetime64('2020-03-15'), raw_dates, averages),2)
            t2_reviewcount = int(np.interp(np.datetime64('2020-05-25'), raw_dates, num_reviews))
            t2_average = round(np.interp(np.datetime64('2020-05-25'), raw_dates, averages),2)
            t3_reviewcount = int(np.interp(np.datetime64('2020-06-25'), raw_dates, num_reviews))
            t3_average = round(np.interp(np.datetime64('2020-06-25'), raw_dates, averages),2)
            t4_reviewcount = int(np.interp(np.datetime64('2020-12-25'), raw_dates, num_reviews))
            t4_average = round(np.interp(np.datetime64('2020-12-25'), raw_dates, averages),2)

            print({restaurant_name:(total_reviews, final_average, t0_reviewcount, t0_average, t1_reviewcount, t1_average, t2_reviewcount, t2_average, t3_reviewcount, t3_average, t4_reviewcount, t4_average)})
            tdata[restaurant_name] = [total_reviews, final_average, t0_reviewcount, t0_average, t1_reviewcount, t1_average, t2_reviewcount, t2_average, t3_reviewcount, t3_average, t4_reviewcount, t4_average]

            print(f'done with {file}')

    print(tdata)
    # writes file for tdata
    filename = f'tdata/{city}-tdata.csv'
    with open(filename, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["restaurant_name", 'total_num_reveiws', 'final_average', "t0_reviewcount", "t0_averagerating", "t1_reviewcount", "t1_averagerating", "t2_reviewcount", "t2_averagerating", "t3_reviewcount", "t3_averagerating", "t4_reviewcount", "t4_averagerating"])
        for key in tdata.keys():
            data = tdata[key]
            csvwriter.writerow([key, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]])
    
    # creates same visualization as above for all reviews
    sorted_all_reviews = sorted(all_reviews, key = lambda x:x[1])
    sum = 0
    count = 0
    averaged_all_reviews = []

    # creates running average for reviews
    for row in sorted_all_reviews:
        date = row[0]
        converted_date = row[1]
        rating = row[2]
        review = row[3]
        restaurant = row[4]

        sum += rating
        count += 1

        average = round(sum/count, 2)
        averaged_all_reviews.append([date, converted_date, rating, average, review, restaurant])

    dates = dates = [DT.datetime.strptime(str(int(review[1])),'%Y%m%d') for review in averaged_all_reviews]
    num_reviews = range(1, len(averaged_all_reviews) + 1)
    averages = [x[3] for x in averaged_all_reviews]

    fig, ax1 = plt.subplots()

    ax2 = ax1.twinx()
    ax1.plot(dates, num_reviews, 'r-')
    ax2.plot(dates, averages, 'b-')

    xfmt = mdates.DateFormatter('%Y-%m-%d')
    ax1.xaxis.set_major_formatter(xfmt)
    xticks = ['2008-01-01', '2009-01-01', '2010-01-01', '2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01', '2015-01-01', '2016-01-01', '2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01', '2020-05-25', '2021-01-01', '2022-01-01']
    ax1.set_xticks(xticks)
    ax1.set_xticklabels(['2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', 'May 25,\n2020', '2021', '2022'])
    plt.xticks(rotation=25)

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Reviews', color='r')
    ax2.set_ylabel('Average Star Rating', color='b')
    ax1.set_title('all reviews')

    plt.axvline(DT.datetime(2020, 3, 15), color='g', linestyle="--", label='begining of Covid-19 Pandemic')
    plt.axvline(DT.datetime(2020, 5, 25), color='k', linestyle='--', label='murder of Gorge Floyd')
    plt.tight_layout()
    plt.show()

    return averaged_all_reviews

# creates review database
def create_database():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/reviews.db')
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS allReviews
        (objectID STRING PRIMARY KEY, city STRING, restaurant STRING, date STRING, convertedDate INTEGER, rating INTEGER, review STRING)
        """
    )
    conn.commit()
    return cur, conn

def create_city_database(cur, conn, city):
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {city}
        (objectID STRING PRIMARY KEY, restaurant STRING, date STRING, convertedDate INTEGER, rating INTEGER, average FLOAT, review STRING)
        """
    )
    conn.commit()

# updates database
def populate_reviews(cur, conn, reviews, city, city_code):
    for review in reviews:
        objid = city_code + str(reviews.index(review))
        date = review[0]
        converted_date = review[1]
        rating = review[2]
        average = review[3]
        r = review[4]
        restaurant = review[5]

        cur.execute(
            f"""
            INSERT OR IGNORE INTO {city} (objectID, restaurant, date, convertedDate, rating, average, review)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (objid, restaurant, date, converted_date, rating, average, r)
        )
        conn.commit()

        cur.execute(
            """
            INSERT OR IGNORE INTO allReviews (objectID, city, restaurant, date, convertedDate, rating, review)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (objid, city, restaurant, date, converted_date, rating, r)
        )
        conn.commit()

# finds 30 most frequent, non-common, words in all reviews for given city
def nlp(reviews):
    text_reviews = [r[4] for r in reviews]
    words = []
    for r in text_reviews:
        for word in r.split(' '):
            words.append(word.lower().replace('!', '').replace('.','').replace('?', '').replace(',',''))

    stopwords = nltk.corpus.stopwords.words('english')
    allWordExceptStopDist = nltk.FreqDist(w.lower() for w in words if w not in stopwords)
    return allWordExceptStopDist.most_common(30)

def main():
    # city codes: Detroit-001, Chicago-002, New York-003, LA black-owned-004, LA not-black-owned-005
    reviews = create_visualizations('new-york')
    cur, conn = create_database()
    create_city_database(cur, conn, 'newYork')
    populate_reviews(cur, conn, reviews, 'newYork', '003')
    print(nlp(reviews))

if __name__ == '__main__':
    main()