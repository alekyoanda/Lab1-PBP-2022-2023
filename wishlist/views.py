import datetime
import json
from wishlist.utils import write_json
from django.shortcuts import render, redirect
from wishlist.models import BarangWishlist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core import serializers
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

# Create your views here.
@login_required(login_url='/wishlist/login')
def show_wishlist(request):
    data_barang_wishlist = BarangWishlist.objects.all()
    context = {
        'list_barang': data_barang_wishlist,
        'nama': 'Kak Cinoy',
        'last_login': request.COOKIES['last_login'],
    }
    return render(request, "wishlist.html", context)

@login_required(login_url='/wishlist/login')
def show_wishlist_ajax(request):
    data_barang_wishlist = BarangWishlist.objects.all()
    context = {
        'list_barang': data_barang_wishlist,
        'nama': 'Kak Cinoy',
        'last_login': request.COOKIES['last_login'],
    }
    return render(request, "wishlist_ajax.html", context)

def json_to_database_async(request):
    data_from_fetch = json.load(request)

    nama_barang = data_from_fetch['nama_barang']
    harga_barang = int(data_from_fetch['harga_barang'])
    deskripsi = data_from_fetch['deskripsi']

    new_wishlist = BarangWishlist.objects.create(nama_barang=nama_barang, harga_barang=harga_barang, deskripsi=deskripsi)

    data = {
        "model": "wishlist.barangwishlist",
        "pk": new_wishlist.id,
        "fields":{
            "nama_barang": nama_barang,
            "harga_barang": harga_barang,
            "deskripsi": deskripsi
        }
    }

    write_json(data)
    
    return JsonResponse(data)

def show_xml(request):
    data = BarangWishlist.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = BarangWishlist.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_json_by_id(request, id):
    data = BarangWishlist.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = BarangWishlist.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Akun telah berhasil dibuat!')
            return redirect('wishlist:login')
    
    context = {'form':form}
    if request.user.is_authenticated:
        return redirect(reverse('wishlist:show_wishlist')) 
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) # melakukan login terlebih dahulu
            response = HttpResponseRedirect(reverse("wishlist:ajax")) # membuat response
            response.set_cookie('last_login', str(datetime.datetime.now())) # membuat cookie last_login dan menambahkannya ke dalam response
            return response
        else:
            messages.info(request, 'Username atau Password salah!')
    context = {}
    if request.user.is_authenticated:
        return redirect(reverse('wishlist:ajax')) 
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('wishlist:login'))
    response.delete_cookie('last_login')
    return response
