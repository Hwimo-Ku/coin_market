from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

cluster = MongoClient("mongodb+srv://hmku1:gubon00909!K@cluster0.zemkgul.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
#db
selling_post = db['selling_post']
transacted_post = db['transacted_post']
user_info = db['user_info']

app = Flask(__name__)
app.secret_key = 'secret'

# Home page
@app.route('/')
def home():
    # TODO: add logic to display current coin price and trend
    posts = selling_post.find()
    if 'id' in session:
        #여기에 이제 로그인 되어있을 때의 코드
        user_id = session['id']
        return render_template('home.html', user_id=user_id, posts=posts)
    else:
        #여기에 이제 로그인 안 되어있을 때의 코드
        return render_template('home.html', posts=posts)
    
    

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
        # TODO: add logic to sign the user out
        flash('로그 아웃 완료!')
        return redirect(url_for('home'))
    else:
        flash('로그인된 상태가 아닙니다.')
        return redirect(url_for('home'))

# 구매
@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if session.get('id'):
        post_id = request.form.get('post_id')
        post = selling_post.find_one({'_id': ObjectId(post_id)})
        if post:
            buyer_id = session['id']
            buyer = user_info.find_one({'id': buyer_id})
            seller = user_info.find_one({'id': post['user']})
            
            total_price = int(post['price']) * int(post['coin'])
            
            if buyer and seller and buyer['money'] >= total_price:
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
                transacted_post.insert_one(post)
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


if __name__ == '__main__':
    app.run(debug=True)


