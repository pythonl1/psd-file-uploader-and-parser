# -*- coding: utf-8 -*-
import os
import uuid
import json
import base64
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.core.urlresolvers import reverse

from myproject.myapp.models import Document
from myproject.myapp.forms import DocumentForm
from psd_tools import PSDImage
from psd_tools.constants import BlendMode
from psd_tools.user_api import pil_support

def list(request):
    # Handle file upload!
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST!
            return HttpResponseRedirect(reverse('myproject.myapp.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form!



    # Load documents for the list page!
    documents = Document.objects.all()
    if documents:
        for document in documents:
            print ( document.docfile.url)
            psd =PSDImage.load(os.path.join(os.path.dirname(__file__), "/myproject" + document.docfile.url))
            layer_details = psd.layers
            items = []

            psd_header = psd.header
            try:
                os.makedirs(os.path.join(os.path.dirname(__file__), "/myproject/" + 'media/' + str(document.docfile.name).rsplit('.', 1)[0]))

            except OSError:
                pass
            
            filename = str(document.docfile.name).rsplit('.', 1)[0] + '.json'
            f = open(filename, 'a')



            # save  the flatened image in png format in a directory!
            merged_image = psd.as_PIL()
            merged_image_filename = str(document.docfile.name).rsplit('.', 1)[0] + '.png'
            merged_image.save(os.path.join(os.path.dirname(__file__), "/myproject/" + 'media/' + str(document.docfile.name).rsplit('.', 1)[0] + '/' + merged_image_filename))



            # for loop to extract layer and its information from the psd uploaded
            for layer_count in layer_details:


                # empty dict for storing layer information
                item = {}


                # psd header details viz falana and dekana are extracted here!
                item['psdheader_details'] = psd_header




                # layer names
                item['layer_name'] = layer_count.name




                # convert layer as an image for further processing in future.
                layer_image = layer_count.as_PIL()

                item['asdf'] = str((base64.b64decode((layer_image.tobytes()).decode("utf-8"))))
                print (item['asdf'])
                foo = open('raw_data.json', 'w')
                foo.write(json.dumps(item['asdf']))
                foo.close()


                layer_image_filename = str(layer_count.name) + '.png'
                

                # save layer in a paricular directory.
                layer_image.save(os.path.join(os.path.dirname(__file__), "/myproject/" + 'media/' + str(document.docfile.name).rsplit('.', 1)[0] + '/' + layer_image_filename))



            # write layer informations to a jason file.
            f.write(str(items) + '\n')
            f.close()

            #json_data = str(items)
            #return HttpResponse(json.dumps(json_data), content_type="text/json")
   

    # Render list page with the documents and the form.
    return render_to_response(
        'list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
