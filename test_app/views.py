from django.shortcuts import render
from django.http import JsonResponse

import json

def test_view(request):
	x = {
 	 "bitstamp": [
 		{
			"pairing": 'xrpbtc',
			"currencies": ['XRP', 'BTC'],
			"rate1": '0.00012366',
			"rate2": '0.00012406',
			"date": '12/18/2017 12:00:00'
		},
		{
			"pairing": 'bchbtc',
			"currencies": ['BCH', 'BTC'],
			"rate1": '0.00012354',
			"rate2": '0.00012389',
			"date": '12/18/2017 12:00:00'
		}
	],
	"bittrex": [
		{
			"pairing": 'xrpbtc',
			"currencies": ['XRP', 'BTC'],
			"rate1": '0.00012366',
			"rate2": '0.00012406',
			"date": '12/18/2017 12:00:00'
		},
		{
			"pairing": 'bchbtc',
			"currencies": ['BCH', 'BTC'],
			"rate1": '0.00012354',
			"rate2": '0.00012389',
			"date": '12/18/2017 12:00:00'
		}
	],
	"kraken": [
		{
			"pairing": 'xrpbtc',
			"currencies": ['XRP', 'BTC'],
			"rate1": '0.00012366',
			"rate2": '0.00012406',
			"date": '12/18/2017 12:00:00'
		},
		{
			"pairing": 'bchbtc',
			"currencies": ['BCH', 'BTC'],
			"rate1": '0.00012354',
			"rate2": '0.00012389',
			"date": '12/18/2017 12:00:00'
		}
	]}
	return JsonResponse(x)
