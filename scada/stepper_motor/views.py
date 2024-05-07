import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.conf import settings
from stepper_motor import utils, models


def control_mode(request):
        
    return render(
                    request,
                    "stepper_motor/control_mode.html",
                    {
                    }
    )


def data_table(request):
    new_state = utils.StateManager.load_state()

    return render(
                    request,
                    "stepper_motor/data_table.html",
                    {
                        "newState": new_state
                    }
    )
