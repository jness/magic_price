# Create your views here.

from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render

import urllib
from urllib2 import urlopen, quote, Request
from re import compile, search

def index(request):
    if request.method == 'POST':
        total_cost = []
        data = request.POST['deck']
        results = []
        if data:
            for line in data.split('\n'):
                # grab the first element and check its a int
                c = search('^\d*', line)
                if c:
                    count = c.group(0)
                else:
                    raise Http404

                # pull card name
                card = ' '.join(line.split()[1:])
                if not card:
                    continue
               
                # try to get prices fro TCGPlayer
                quoted_card = quote(card)
                u = urlopen('http://magic.tcgplayer.com/db/wp-ch.asp?CN=%s' % quoted_card)
                try:
                    prices = compile('\$(\d*.\d\d)\r\n[\t]*</div>').findall(u.read())
                    lowest_price = prices[2]
                except IndexError:
                    message = 'Unable to get card <b>%s</b>, please check spelling' % card
                    return render(request, 'index.html', {'error': message, 'data': data}) 
                results.append({'name': card, 
                                'count': count, 
                                'price_each': lowest_price, 
                                'price': '%.2f' % (float(lowest_price) * int(count))})
                total_cost.append('%.2f' % (float(lowest_price) * int(count)))

            deck_total = ('%.2f' % (sum(float(i) for i in total_cost)))
            return render(request, 'list.html', {'results': results, 'total': deck_total})

        else:
            raise Http404

    else:
        return render(request, 'index.html')


def gatherer_lookup(request, card):
    page = urlopen('http://gatherer.wizards.com/Pages/Default.aspx').read()
    viewstat = compile('<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*)"').findall(page)
    eventval = compile('<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*)"').findall(page)

    button = 'ctl00$ctl00$MainContent$Content$SearchControls$searchSubmitButton'
    searchbox = 'ctl00$ctl00$MainContent$Content$SearchControls$CardSearchBoxParent$CardSearchBox'
    post = {button: 'Search', searchbox: card, '__VIEWSTATE': viewstat[0], '__EVENTVALIDATION': eventval[0]}

    req = Request('http://gatherer.wizards.com/Pages/Default.aspx')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_data(urllib.urlencode(post))
    results = urlopen(req)
    return HttpResponseRedirect(results.geturl())
