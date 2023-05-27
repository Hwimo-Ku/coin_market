from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

cluster = MongoClient("mongodb+srv://hmku1:gubon00909!K@cluster0.zemkgul.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
#db
selling_post = db['selling_post']
transacted_post = db['transacted_post']
user_info = db['user_info']
market_data = db['market_data']

app = Flask(__name__)
app.secret_key = 'secret'

# Home page
@app.route('/')
def home():
    # TODO: add logic to display current coin price and trend
    posts = selling_post.find()
    transaction_data = transacted_post.find()
    
    market_coin = market_data.find_one({'user' : 'marketplace'})
    
    
    # recent transition
    recent_transitions = list(transacted_post.find().sort('_id', -1).limit(10))
    recent_transitions_serializable = []
    for transition in recent_transitions:
        recent_transitions_serializable.append({
            'coin': transition['coin'],
            'price': transition['price'],
            'timestamp':transition['timestamp']
        })
    
    if 'id' in session:
        #여기에 이제 로그인 되어있을 때의 코드
        user_id = session['id']
        user_info_data = user_info.find_one({'id': user_id})

        return render_template('home.html', user_id=user_id, posts=posts, user_info=user_info_data, transactions=transaction_data, recent_transitions=recent_transitions_serializable, market=market_coin)
    else:
        #여기에 이제 로그인 안 되어있을 때의 코드
        return render_template('home.html', posts=posts, transactions=transaction_data, recent_transitions=recent_transitions_serializable, market=market_coin)
    
    

# 회원가입 페이지로 이동
@app.route('/signup', methods=['POST'])
def signup():
    if 'id' in session:
        flash('이미 로그인되어있습니다. 로그아웃 후 접근해주세요!')
        user_id = session['id']
        return render_template('home.html', user_id=user_id)
    else:
        return render_template('signup.html')

# 회원가입 제출 버튼 눌렀을 때
@app.route('/submit_signup', methods=['GET','POST'])
def submit_signup():
    # Get the form data from the request
        id = request.form['id']
        password = request.form['password']
        check_password = request.form['check_password']

        # 이미 가입된 것인지 확인하기
        existing_user = user_info.find_one({'id': id})
        if existing_user:
            flash('이미 가입된 사용자입니다.')
            return render_template('signup.html')

        # user 구성
        if (password != "") and (password == check_password):
            new_user = {
            'id': id,
            'password': password,
            'money':0,
            'coin':0
            }
            # DB에 데이터 넣기
            user_info.insert_one(new_user)
            flash('가입이 완료되었습니다. 홈으로 돌아갑니다. 로그인 후 사용해주세요.')
            # home으로 redirect
            return redirect(url_for('home'))
        else:
            flash('비밀번호가 다릅니다.')
            return render_template('signup.html')
            

# go to Sign in page
@app.route('/signin', methods=['GET','POST'])
def signin():
    if 'id' in session:
        flash('이미 로그인되어있습니다.')
        user_id = session['id']
        return render_template('home.html', user_id=user_id)
    return render_template('signin.html')
    
#로그인 버튼을 눌렀을 때    
@app.route('/submit_signin', methods=['GET','POST'])
def submit_signin():
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']

        # 가입된 것인지 확인하기
        existing_user = user_info.find_one({'id': id})
        if existing_user:
            if password == existing_user["password"]:
                session['id'] = request.form['id']
                flash('로그인 성공!')
                return redirect(url_for('home'))
            else:
                flash('비밀번호가 다릅니다! 다시 시도해주세요!')
        else:
            flash('가입되지 않은 사용자입니다.')
    else:
        return render_template('signin.html')

# Sign out
@app.route('/signout', methods=['POST'])
def signout():
    if 'id' in session:
        session.pop('id', None)
        flash('로그 아웃 완료!')
        return redirect(url_for('home'))
    else:
        flash('로그인된 상태가 아닙니다.')
        return redirect(url_for('home'))


# market coin 구매
@app.route('/buy_market_coin', methods=['GET', 'POST'])
def buy_market_coin():
    if session.get('id'):
        market_coin = market_data.find_one({'user' : 'marketplace'})
        if market_coin:
            buyer_id = session['id']
            buyer = user_info.find_one({'id': buyer_id})
            
            amount = int(request.form['amount'])
            total_price = int(market_coin['price']) * amount
            
            if amount <= market_coin['coin']:
                if buyer and (buyer['money'] >= total_price):
                    # Update buyer's money and coin
                    user_info.update_one(
                        {'id': buyer_id},
                        {'$inc': {'money': -total_price, 'coin': amount}}
                    )
                    # Update market's coin
                    market_data.update_one(
                        {'user': "marketplace"},
                        {'$inc': {'coin': -amount}}
                    )
                    # Add transaction to transacted_post collection
                    transacted_time = datetime.now()
                    transacted_time_iso = transacted_time.isoformat()
                    transaction = {
                        'user': buyer_id,
                        'coin': amount,
                        'price': 100,
                        'timestamp':transacted_time_iso
                    }
                    transacted_post.insert_one(transaction)
                    flash('구매가 완료되었습니다.')
                else:
                    flash('잔액이 부족하거나 사용자 정보를 찾을 수 없습니다.')
            else:
                flash('입력한 개수가 잔여량보다 많습니다.')
        else:
            flash('존재하지 않는 게시물입니다.')
    else:
        flash('로그인 후 이용해주세요!')
    return redirect(url_for('home'))
    
# 구매
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if session.get('id'):
        post_id = request.form.get('post_id')
        user_id = request.form.get('user_id')
        if user_id == session['id']:
            flash('본인 소유의 코인입니다.')
            return redirect(url_for('home'))
        post = selling_post.find_one({'_id': ObjectId(post_id)})
        if post:
            buyer_id = session['id']
            buyer = user_info.find_one({'id': buyer_id})
            seller = user_info.find_one({'id': post['user']})
            
            total_price = int(post['price']) * int(post['coin'])
            
            if buyer and seller and (buyer['money'] >= total_price):
                # Update buyer's money and coin
                user_info.update_one(
                    {'id': buyer_id},
                    {'$inc': {'money': -total_price, 'coin': int(post['coin'])}}
                )
                # Update seller's money and coin
                user_info.update_one(
                    {'id': post['user']},
                    {'$inc': {'money': total_price, 'coin': int(-post['coin'])}}
                )
                # Add transaction to transacted_post collection
                transacted_time = datetime.now()
                transacted_time_iso = transacted_time.isoformat()
                transaction = {
                    'user':buyer_id,
                    'coin':post['coin'],
                    'price':post['price'],
                    'timestamp':transacted_time_iso
                }
                transacted_post.insert_one(transaction)
                # Delete the post from selling_post collection
                selling_post.delete_one({'_id': ObjectId(post_id)})
                flash('구매가 완료되었습니다.')
            else:
                flash('잔액이 부족하거나 사용자 정보를 찾을 수 없습니다.')
        else:
            flash('존재하지 않는 게시물입니다.')
    else:
        flash('로그인 후 이용해주세요!')
    return redirect(url_for('home'))

#판매
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if session.get('id'):
        if request.method == 'POST':
            coin_quantity = int(request.form['coin_quantity'])
            price = int(request.form['price'])
            
            user = user_info.find_one({'id':session['id']})
            
            transacted_time = datetime.now()
            transacted_time_iso = transacted_time.isoformat()
            
            if coin_quantity <= int(user['coin']):
                # Create a new post
                new_post = {
                    'user': session['id'],
                    'coin': coin_quantity,
                    'price': price,
                    'timestamp':transacted_time_iso
                }
            
                # Insert the new post into the selling_post collection
                selling_post.insert_one(new_post)
                flash('판매 등록이 완료되었습니다.')
            else:
                flash('보유한 코인 수가 부족합니다.')
            return redirect(url_for('home'))
    else:
        flash('로그인 후 이용해주세요!')
    return redirect(url_for('home'))
            
# go to my page
@app.route('/mypage', methods=['GET','POST'])
def mypage():
    if 'id' in session:
        user_id = session['id']
        user_info_data = user_info.find_one({'id':user_id})
        return render_template('mypage.html', user_id=user_id, user_info=user_info_data)
    else:
        flash('로그인 후 사용해주세요!')
        return redirect(url_for('signin'))
        
        
# Add or Withdraw money
@app.route('/add_withdraw', methods=['POST'])
def add_withdraw():
    if 'id' in session:
        user_id = session['id']
        amount = int(request.form['withdraw_amount'])

        user = user_info.find_one({'id': user_id})

        if user:
            if request.form['action'] == 'Withdraw':
                if amount <= user['money']:
                    # Update the user's money
                    user_info.update_one(
                        {'id': user_id},
                        {'$inc': {'money': -amount}}
                    )
                    flash('출금이 완료되었습니다.')
                else:
                    flash('잔액이 부족합니다.')
            elif request.form['action'] == 'Add':
                # Update the user's money
                user_info.update_one(
                    {'id': user_id},
                    {'$inc': {'money': amount}}
                )
                flash('입금이 완료되었습니다.')
            else:
                flash('올바른 작업이 아닙니다.')
        else:
            flash('사용자 정보를 찾을 수 없습니다.')
    else:
        flash('로그인 후 이용해주세요!')

    return redirect(url_for('mypage'))

@app.route('/home', methods=['POST'])
def go_home():
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)