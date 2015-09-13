# -*- coding: utf-8 -*-
import os
import uuid
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from myproject.myapp.models import Document
from myproject.myapp.forms import DocumentForm
from psd_tools import PSDImage
from psd_tools.constants import BlendMode

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
            psd_header = psd.header
            items = []

            try:
                os.makedirs(os.path.join(os.path.dirname(__file__), "/myproject" + '/image_data_raw'))

            except OSError:
                pass
            
            filename = 'image_data_j' + str(uuid.uuid4()) + '.json'
            f = open(filename, 'a')



            # save  the flatened image in png format in a directory!
            merged_image = psd.as_PIL()
            merged_image_filename = 'merged_image'+ str(uuid.uuid4()) +'.png'
            merged_image.save(os.path.join(os.path.dirname(__file__), "/myproject/" + 'image_data_raw/' + merged_image_filename))



            # for loop to extract layer and its information from the psd uploaded
            for layer_count in layer_details:


                # empty dict for storing layer information
                item = {}


                # psd header details viz falana and dekana are extracted here!
                item['psdheader_details'] = psd_header


                # convert layer as an image for further processing in future.
                layer_image = layer_count.as_PIL()
                layer_image_filename ='layer' + str(uuid.uuid4()) + '.png'
                

                # save layer in a paricular directory.
                layer_image.save(os.path.join(os.path.dirname(__file__), "/myproject/" + 'image_data_raw/' + layer_image_filename))



                # information related to each layer is extracted here!
                # layer name is extracted here!
                if (len(layer_count.name) != 0):
                    item['layer_name'] = layer_count.name
                else:
                    pass
                

                # layer bbox details is extracted here!
                item['layer_bbox'] = layer_count.bbox
                

                # layer bbox height
                if (layer_count.bbox.height != None):
                    item['layer_bbox_height'] = layer_count.bbox.height
                else:
                    pass


                # layer bbox width
                if ((layer_count.bbox.width) != None):
                    item['layer_bbox_width'] = layer_count.bbox.width
                else:
                    pass


                # layer visibilty is read here!
                item['layer_visibility'] = layer_count.visible


                # layer blend mode 
                item['layer_blendmode'] = layer_count.blend_mode



                def textSizeColor(layer):
                    if layer._tagged_blocks.has_key('TySh') :
                        #pprint.pprint( layer._tagged_blocks['TySh'] )
                        rawData = layer._tagged_blocks['TySh'].text_data.items[-1][-1]
                        rawDataValue = rawData.value

                        propDict= {'FontSet':'','Text':'','FontSize':'','A':'','R':'','G':'','B':''}
                        getFontAndColorDict(propDict,rawDataValue)
                        #Then just index into the dictionary to get the values
                        item['image_layer_text'] = propDict['Text']
                        item['image_layer_fontset'] = propDict['FontSet']
                        item['image_layer_fontsize'] = propDict['FontSize']

                        return propDict
                        #return (propDict['FontSet'], propDict['FontSize'])
                    else:
                        return None


                # append layer info to the list.
                items.append(item)


            # write layer informations to a jason file.
            f.write(str(items) + '\n')
            f.close()


    # Render list page with the documents and the form.
    return render_to_response(
        'list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
