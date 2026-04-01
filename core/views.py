from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
import yfinance as yf
from decimal import Decimal
from .models import Stock, Portfolio, Transaction
from django import forms

# --- HELPER: Calculates global Net Worth and Cash ---
def get_base_context(user):
    portfolio_qs = Portfolio.objects.filter(user=user, shares__gt=0)
    context = {
        'virtual_cash': round(user.virtual_cash, 2),
        'username': user.username
    }
    return context, portfolio_qs

# --- VIEW 1: Market Floor (Dashboard) ---
POPULAR_STOCKS = [
    {'symbol': 'AAPL', 'name': 'Apple Inc.'},
    {'symbol': 'MSFT', 'name': 'Microsoft Corp.'},
    {'symbol': 'NVDA', 'name': 'NVIDIA Corp.'},
    {'symbol': 'TSLA', 'name': 'Tesla Inc.'},
    {'symbol': 'AMZN', 'name': 'Amazon.com'},
    {'symbol': 'GOOGL', 'name': 'Alphabet (Google)'},
    {'symbol': 'META', 'name': 'Meta Platforms'},
    {'symbol': 'NFLX', 'name': 'Netflix Inc.'},
    {'symbol': 'DIS', 'name': 'Walt Disney Co.'},
    {'symbol': 'NKE', 'name': 'Nike Inc.'},
    {'symbol': 'SBUX', 'name': 'Starbucks'},
    {'symbol': 'AMD', 'name': 'Advanced Micro Devices'}
]

@login_required(login_url='login')
def dashboard(request):
    symbol = request.GET.get('ticker', 'AAPL').upper()
    
    # Get the basic navbar context
    base_context, portfolio_qs = get_base_context(request.user)
    
    context = {
        **base_context,
        'symbol': symbol,
        'popular_stocks': POPULAR_STOCKS, 
    }
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        current_price = info.last_price
        prev_close = info.previous_close
        price_change = current_price - prev_close
        
        context.update({
            'current_price': round(current_price, 2), 
            'price_change': round(price_change, 2),
            'percent_change': round((price_change / prev_close) * 100, 2),
        })
    except Exception:
        context['error_message'] = f"Unable to fetch live data for '{symbol}'."
    
    return render(request, 'core/dashboard.html', context)

# --- VIEW 2: Cargo Hold (Portfolio) ---
@login_required(login_url='login')
def portfolio_view(request):
    base_context, portfolio_qs = get_base_context(request.user)
    portfolio_data = []
    total_stock_value = Decimal('0.00')

    for item in portfolio_qs:
        try:
            t = yf.Ticker(item.stock.symbol)
            live_price = Decimal(str(round(t.fast_info.last_price, 2)))
            pos_val = live_price * item.shares
            total_stock_value += pos_val
            portfolio_data.append({
                'symbol': item.stock.symbol, 'shares': item.shares,
                'live_price': live_price, 'position_value': pos_val
            })
        except: pass

    net_worth = round(base_context['virtual_cash'] + total_stock_value, 2)
    context = {**base_context, 'net_worth': net_worth, 'portfolio_data': portfolio_data}
    
    return render(request, 'core/portfolio.html', context)

# --- VIEW 3: Flight Ledger (History) ---
@login_required(login_url='login')
def history_view(request):
    base_context, portfolio_qs = get_base_context(request.user)
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')[:20]
    
    initial_capital = Decimal('10000.00') # Your starting cash
    total_stock_value = Decimal('0.00')
    profit_breakdown = []
    
    for item in portfolio_qs:
        try:
            t = yf.Ticker(item.stock.symbol)
            live_price = Decimal(str(round(t.fast_info.last_price, 2)))
            current_value = live_price * item.shares
            total_stock_value += current_value
            
            # Calculate average buy price (Cost Basis)
            buys = Transaction.objects.filter(user=request.user, stock=item.stock, action='buy')
            total_spent = sum((buy.shares * buy.price for buy in buys), Decimal('0.00'))
            total_bought_shares = sum((buy.shares for buy in buys), 0)
            
            avg_cost = total_spent / Decimal(total_bought_shares) if total_bought_shares > 0 else Decimal('0.00')
            cost_basis = avg_cost * Decimal(item.shares)
            
            # Calculate Profit / Loss
            unrealized_pl = current_value - cost_basis
            
            profit_breakdown.append({
                'symbol': item.stock.symbol,
                'shares': item.shares,
                'avg_cost': round(avg_cost, 2),
                'live_price': round(live_price, 2),
                'total_value': round(current_value, 2),
                'unrealized_pl': round(unrealized_pl, 2),
                'is_profit': unrealized_pl >= 0
            })
        except: 
            pass
            
    net_worth = round(base_context['virtual_cash'] + total_stock_value, 2)
    total_profit = round(net_worth - initial_capital, 2)
    
    context = {
        **base_context, 
        'recent_transactions': recent_transactions, 
        'net_worth': net_worth,
        'total_profit': total_profit,
        'initial_capital': initial_capital,
        'profit_breakdown': profit_breakdown
    }
    
    return render(request, 'core/history.html', context)

# --- ACTION: Trade Logic ---
@login_required(login_url='login')
def trade(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol').upper()
        action = request.POST.get('action') 
        shares = int(request.POST.get('shares', 0))
        
        if shares > 0:
            try:
                price = Decimal(str(round(yf.Ticker(symbol).fast_info.last_price, 2)))
                total_cost = price * shares
                stock_obj, _ = Stock.objects.get_or_create(symbol=symbol, defaults={'company_name': symbol})
                portfolio_obj, _ = Portfolio.objects.get_or_create(user=request.user, stock=stock_obj)
                
                if action == 'buy' and request.user.virtual_cash >= total_cost:
                    request.user.virtual_cash -= total_cost
                    request.user.save()
                    portfolio_obj.shares += shares
                    portfolio_obj.save()
                    Transaction.objects.create(user=request.user, stock=stock_obj, action='buy', shares=shares, price=price)
                elif action == 'sell' and portfolio_obj.shares >= shares:
                    request.user.virtual_cash += total_cost
                    request.user.save()
                    portfolio_obj.shares -= shares
                    portfolio_obj.save()
                    Transaction.objects.create(user=request.user, stock=stock_obj, action='sell', shares=shares, price=price)
            except: pass 
    return redirect('dashboard')


# =========================================================
# --- NEW AUTHENTICATION VIEWS ---
# =========================================================

User = get_user_model()

class GalaxyRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    # This widget automatically turns the input into a clickable calendar!
    date_of_birth = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}) 
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # The order here is exactly how it will appear on the screen
        fields = ("username", "first_name", "last_name", "email", "phone_number", "date_of_birth")

    # Custom validation to double-check that the email is truly unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Transmission failed: This email is already registered to another commander.")
        return email

def register(request):
    if request.method == 'POST':
        form = GalaxyRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically log them in after registering
            return redirect('dashboard')
    else:
        form = GalaxyRegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')