import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

URL = "https://chieuphimquocgia.com.vn/movies"

# Gửi request đến trang web
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}
response = requests.get(URL, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    date_buttons = soup.select("button[role='tab']")
    movie_data = {
        "hôm nay": [],
        "ngày mai": [],
        "ngày kia": [],
        "khác": []
    }

    def format_time(time_str):
        try:
            hour, minute = map(int, time_str.split(":"))
            return f"{hour} giờ {minute} phút"
        except ValueError:
            return time_str  

    for button in date_buttons:
        date_text = button.text.strip()
        try:
            date_obj = datetime.strptime(date_text.split(",")[-1].strip(), "%d-%m-%Y").date()
        except ValueError:
            continue  
        
        if date_obj == today:
            day_category = "hôm nay"
        elif date_obj == tomorrow:
            day_category = "ngày mai"
        elif date_obj == day_after_tomorrow:
            day_category = "ngày kia"
        else:
            day_category = "khác"

        movie_cards = soup.select(".p-4")
        for movie in movie_cards:
            try:
                title = movie.select_one(".font-bold").text.strip()
                description = movie.select_one(".line-clamp-2").text.strip() if movie.select_one(".line-clamp-2") else "Không có mô tả"
                format_ = movie.select_one(".absolute").text.strip() if movie.select_one(".absolute") else "null"
                age_rating = movie.select_one(".text-red-500").text.strip() if movie.select_one(".text-red-500") else "Không có thông tin"

                details = movie.select("p")
                genre = details[0].text.strip() if len(details) > 0 else "null"
                duration = details[1].text.strip() if len(details) > 1 else "null"
                premiere = details[4].text.strip() if len(details) > 4 else "null"

                schedules = [format_time(btn.text.strip()) for btn in movie.select(".flex.items-center.gap-2.mt-2.flex-wrap button")]
                formatted_schedule = " | ".join(schedules) if schedules else "Không có lịch chiếu"

                movie_data[day_category].append({
                    "date": date_text,
                    "title": title,
                    "format": format_,
                    "age_rating": age_rating,
                    "genre": genre,
                    "duration": duration,
                    "release_date": premiere,
                    "description": description,
                    "schedule": formatted_schedule
                })

            except Exception as e:
                print(f"Lỗi khi lấy dữ liệu phim: {e}")

    with open("movies.json", "w", encoding="utf-8") as file:
        json.dump(movie_data, file, ensure_ascii=False, indent=4)

    print("Đã lấy xong dữ liệu phim!")

else:
    print("Lỗi khi tải trang:", response.status_code)
