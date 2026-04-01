from django.shortcuts import render, redirect
import yfinance as yf
from decimal import Decimal
from .models import Stock, Portfolio, Transaction

# --- HELPER: Calculates global Net Worth and Cash ---
def get_base_context(user):
    portfolio_qs = Portfolio.objects.filter(user=user, shares__gt=0)
    context = {
        'virtual_cash': round(user.virtual_cash, 2),
        'username': user.username
    }
    return context, portfolio_qs

# --- VIEW 1: Market Floor (Dashboard) ---
def dashboard(request):
    symbol = request.GET.get('ticker', 'AAPL').upper()
    base_context, portfolio_qs = get_base_context(request.user)
    
    total_stock_value = Decimal('0.00')
    for item in portfolio_qs:
        try:
            t = yf.Ticker(item.stock.symbol)
            live_price = Decimal(str(round(t.fast_info.last_price, 2)))
            total_stock_value += (live_price * item.shares)
        except: pass
    
    net_worth = round(base_context['virtual_cash'] + total_stock_value, 2)
    context = {**base_context, 'net_worth': net_worth, 'symbol': symbol}
    
    try:
        ticker = yf.Ticker(symbol)
        current_price = ticker.fast_info.last_price
        previous_close = ticker.fast_info.previous_close
        price_change = current_price - previous_close
        
        context.update({
            'current_price': round(current_price, 2), 
            'previous_close': round(previous_close, 2),
            'price_change': round(price_change, 2),
            'percent_change': round((price_change / previous_close) * 100, 2),
        })
    except:
        context['error_message'] = f"Could not find data for '{symbol}'."
    
    return render(request, 'core/dashboard.html', context)

# --- VIEW 2: Cargo Hold (Portfolio) ---
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