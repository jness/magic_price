
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from deck_price.models import Decks

from  hashlib import md5
from urllib import urlencode
from urllib2 import urlopen, quote, Request
from re import compile, search

def index(request):
    '''The main function for the app'''

    # check if this is a deck lookup
    try:
        deck_hash = request.GET['hash']
        try:
            obj = Decks.objects.get(hash=deck_hash)
            data = obj.post
        except ObjectDoesNotExist:
            raise Http404
    except:
        data = ''
    
    # If we have POST data we should attempt lookup
    # else send them to home page
    if not data:
        try:
            data = request.POST['deck']
        except:
            return render(request, 'index.html')

    # a few list to hold data
    total_cost = []
    message = []
    results = []
    clean_data = ''

    # check our POST by name deck contains data
    # else raise a 404 page
    if data:
        # split input on new line chara
        for line in data.split('\n'):

            # ignore empty lines
            if line.isspace() or not line:
                continue

            # perform a search on the 1 character
            # and be sure they are decimals
            c = search('^(\d+)', line)
            if c:
                count = c.group(0)
            else:
                raise Http404

            # the card name should be the 2nd elements
            # till the end of line [1:]
            card = ' '.join(line.split()[1:])
            if not card:
                continue

            # lookup card name on TCGPlayer's Wordpress API page
            quoted_card = quote(card)
            u = urlopen('http://magic.tcgplayer.com/db/wp-ch.asp?CN=%s' % quoted_card)
            try:
                # try to per prices since even on non existing cards
                # tcgplayer does not return a 404
                prices = compile('\$(\d*.\d\d)\r\n[\t]*</div>').findall(u.read())
                lowest_price = prices[2]
            except IndexError:
                # if a price was not pulled the card failed to lookup (misspelled?)
                # notify the end user
                message.append(card)
                continue

            # create a dict which will be returned to the 
            # django template
            results.append({'name': card.title(), 
                            'count': count, 
                            'price_each': lowest_price, 
                            'price': '%.2f' % (float(lowest_price) * int(count))})
            total_cost.append('%.2f' % (float(lowest_price) * int(count)))

        # using all the total prices add them together as a float,
        # this gives os the total deck cost
        deck_total = ('%.2f' % (sum(float(i) for i in total_cost)))

        # append data to clean_data var,
        # this should avoid multiple cache for same results
        clean_data = clean_data + '%s %s\n' % (count, card.title())

        # only create cache if no errors were givin
        if not message:
            # create a unique hash of our data
            # and add to sqlite database if new item
            deck_hash = md5(clean_data).hexdigest()
            try:
                Decks.objects.get(hash=deck_hash)
            except ObjectDoesNotExist:
                c = Decks(hash=deck_hash, post=clean_data)
                c.save()

            # provide a direct url
            url = 'http://%s/?hash=%s' % (request.META['HTTP_HOST'], deck_hash)
            return render(request, 'list.html', {'results': results, 'total': deck_total, 'short': url})

        else:
            # if we had any error messages return them and send the user 
            # to the home page
            return render(request, 'index.html', {'error': message, 'data': data}) 

    else:
        raise Http404

def gatherer_lookup(request, card):
    '''Using card name attempt to pull up the Gatherer page, 
    if only Wizard had an API.....'''

    # In order to run a search we need to pull gatherers unique hidden fields..
    page = urlopen('http://gatherer.wizards.com/Pages/Default.aspx').read()
    viewstat = compile('<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*)"').findall(page)
    eventval = compile('<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*)"').findall(page)

    # build our post using this unique hidden data
    button = 'ctl00$ctl00$MainContent$Content$SearchControls$searchSubmitButton'
    searchbox = 'ctl00$ctl00$MainContent$Content$SearchControls$CardSearchBoxParent$CardSearchBox'
    post = {button: 'Search', searchbox: card, '__VIEWSTATE': viewstat[0], '__EVENTVALIDATION': eventval[0]}

    # make an automated search request
    req = Request('http://gatherer.wizards.com/Pages/Default.aspx')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_data(urlencode(post))
    results = urlopen(req)

    # redirect the user to the Gatherer page which is hopefully the correct card
    return HttpResponseRedirect(results.geturl())
