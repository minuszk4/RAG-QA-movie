import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def fetch_page(url, headers, timeout=10):
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Lỗi khi tải trang: {e}")
        return None

def parse_date(date_text):
    """Chuyển đổi chuỗi ngày thành đối tượng date.
       Dữ liệu đầu vào có dạng 'Label, dd-mm-yyyy'."""
    try:
        date_part = date_text.split(",")[-1].strip()
        return datetime.strptime(date_part, "%d-%m-%Y").date()
    except ValueError:
        return None

def format_time(time_str):
    try:
        hour, minute = map(int, time_str.split(":"))
        return f"{hour} giờ {minute} phút"
    except ValueError:
        return time_str  

def categorize_date(date_obj, today, tomorrow, day_after_tomorrow):
    if date_obj == today:
        return "hôm nay"
    elif date_obj == tomorrow:
        return "ngày mai"
    elif date_obj == day_after_tomorrow:
        return "ngày kia"
    else:
        return "khác"

def extract_movie_data(soup, date_text):
    movies = []
    movie_cards = soup.select(".p-4")
    for movie in movie_cards:
        try:
            title = movie.select_one(".font-bold").get_text(strip=True) if movie.select_one(".font-bold") else "Không có tiêu đề"
            description = movie.select_one(".line-clamp-2").get_text(strip=True) if movie.select_one(".line-clamp-2") else "Không có mô tả"
            format_tag = movie.select_one(".absolute")
            format_ = format_tag.get_text(strip=True) if format_tag else "null"
            age_rating_tag = movie.select_one(".text-red-500")
            age_rating = age_rating_tag.get_text(strip=True) if age_rating_tag else "Không có thông tin"

            details = movie.select("p")
            genre = details[0].get_text(strip=True) if len(details) > 0 else "null"
            duration = details[1].get_text(strip=True) if len(details) > 1 else "null"
            premiere = details[4].get_text(strip=True) if len(details) > 4 else "null"

            schedule_buttons = movie.select(".flex.items-center.gap-2.mt-2.flex-wrap button")
            schedules = [format_time(btn.get_text(strip=True)) for btn in schedule_buttons]
            formatted_schedule = " | ".join(schedules) if schedules else "Không có lịch chiếu"

            movie_info = {
                "date": date_text,
                "title": title,
                "format": format_,
                "age_rating": age_rating,
                "genre": genre,
                "duration": duration,
                "release_date": premiere,
                "description": description,
                "schedule": formatted_schedule
            }
            movies.append(movie_info)
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu phim: {e}")
    return movies

def scrape_movies(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    page_content = fetch_page(url, headers)
    if not page_content:
        return None

    soup = BeautifulSoup(page_content, "html.parser")
    
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    movie_data = {
        "hôm nay": [],
        "ngày mai": [],
        "ngày kia": [],
        "khác": []
    }
    
    date_buttons = soup.select("button[role='tab']")
    if not date_buttons:
        print("Không tìm thấy nút ngày!")
        return movie_data

    for button in date_buttons:
        date_text = button.get_text(strip=True)
        date_obj = parse_date(date_text)
        if not date_obj:
            continue
        
        day_category = categorize_date(date_obj, today, tomorrow, day_after_tomorrow)
        movies = extract_movie_data(soup, date_text)
        movie_data[day_category].extend(movies)

    return movie_data

def save_movies_data(movie_data, filename="movies.json"):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(movie_data, file, ensure_ascii=False, indent=4)
        print("Đã lưu dữ liệu phim vào", filename)
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu: {e}")

def main():
    url = "https://chieuphimquocgia.com.vn/movies"
    movie_data = scrape_movies(url)
    if movie_data:
        save_movies_data(movie_data)

if __name__ == "__main__":
    main()
