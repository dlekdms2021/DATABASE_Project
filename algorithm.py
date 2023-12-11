import sqlite3
from itertools import product

# 데이터베이스 파일 경로 설정
database_path = "/Users/choiyumin/Desktop/db2023/project.db"

# 데이터베이스 연결
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# 사용자 ID를 동적으로 받을 수 있게 변경
user_id = 5

# 결과를 저장할 변수 초기화
max_combination = None
max_total_cost = 0
items_purchased = False  # 구매 가능한 아이템이 있는지 여부를 확인하는 플래그

try:
    # Users 테이블에서 userId에 해당하는 userName과 totalprice 가져오기
    cursor.execute("SELECT userName, totalprice FROM Users WHERE userId = ?", (user_id,))
    user_result = cursor.fetchone()

    if user_result:
        user_name = user_result[0]
        total_price = user_result[1]

        cursor.execute("SELECT items FROM Items WHERE userId = ?", (user_id,))
        items = [item[0] for item in cursor.fetchall()]

        all_options = []
        for item in items:
            cursor.execute("SELECT goodId, goodName, goodPrice FROM Good WHERE goodName LIKE ?", ('%' + item + '%',))
            options = cursor.fetchall()
            all_options.append(options)

        max_price_length = max(len(str(option[2])) for options in all_options for option in options)
        combination_table = []

        for combo in product(*all_options):
            total_cost = sum(item[2] for item in combo)
            if total_cost <= total_price:
                items_purchased = True
                price_strs = [f"{item[1]}({str(item[2]).rjust(max_price_length)}원)" for item in combo]
                combination = [', '.join(price_strs), f"{str(total_cost).rjust(max_price_length)}원"]
                combination_table.append(combination)
                if total_cost > max_total_cost:
                    max_total_cost = total_cost
                    max_combination = combo  # 최적 조합을 상품 정보와 함께 저장

        # 최적 조합 결과 저장
        if max_combination:
            # UserOptimalCombinations 테이블이 없으면 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS User6 (
                    userId INTEGER,
                    goodId INTEGER,
                    goodName TEXT,
                    goodPrice INTEGER,
                    sumPrice INTEGER
                )
            ''')
            # 기존 데이터 삭제
            cursor.execute("DELETE FROM User6 WHERE userId = ?", (user_id,))
            # 새로운 최적 조합 데이터 삽입
            for good in max_combination:
                cursor.execute("INSERT INTO User6 (userId, goodId, goodName, goodPrice, sumPrice) VALUES (?, ?, ?, ?, ?)",
                               (user_id, good[0], good[1], good[2], max_total_cost))
            conn.commit()

        # 결과 출력
        print(f"User ID: {user_id}, User Name: {user_name}, Total Budget: {total_price}원")
        if items_purchased:
            for combo in combination_table:
                print(combo[0] + " | " + combo[1])
            if max_combination:
                print("\n<최적의 조합>")
                print(', '.join([item[1] for item in max_combination]) + " | " + str(max_total_cost) + "원")
        else:
            print("예산 내에서 구매 가능한 아이템 조합이 없습니다.")
            # UserOptimalCombinations 테이블 생성 및 NULL 값 삽입
            cursor.execute('''
                            CREATE TABLE IF NOT EXISTS User6 (
                                userId INTEGER,
                                goodId INTEGER,
                                goodName TEXT,
                                goodPrice INTEGER,
                                sumPrice INTEGER
                            )
                        ''')
            cursor.execute("DELETE FROM User6 WHERE userId = ?", (user_id,))
            cursor.execute(
                "INSERT INTO User6 (userId, goodId, goodName, goodPrice, sumPrice) VALUES (?, NULL, NULL, NULL, NULL)",
                (user_id,))
            conn.commit()
    else:
        print(f"userId {user_id}에 해당하는 데이터가 Users 테이블에 없습니다.")

except sqlite3.Error as e:
    print(f"데이터베이스 오류: {e}")
except Exception as e:
    print(f"일반 오류: {e}")
finally:
    conn.close()
