from lost.db import model
import numpy as np
from skimage.draw import polygon_perimeter, circle, line
from skimage.color import gray2rgb

def trans_boxes_to(boxes, convert_to='minmax'):
    '''Transform a box from standard lost format into a different format
    
    Args:
        boxes (list of list): Boxes in standard lost format [[xc,yc,w,h],...]
        convert_to (str): *minmax* -> [[xmim,ymin,xmax,ymax]...]
    
    Returns:
        list of list: Converted boxes.
    '''
    old = np.array(boxes)
    new = old.copy()

    if convert_to == 'minmax':
        new[:,[0,1]] = old[:,[0,1]] - old[:,[2,3]] / 2.0
        new[:,[2,3]] = old[:,[0,1]] + old[:,[2,3]] / 2.0
        new[new < 0.0] = 0.0
        new[new > 1.0] = 1.0
        return new
    else:
        raise Exception('Unknown convert_to format: {}'.format(convert_to))

def to_abs(annos, types, img_size):
    '''Convert relative annotation coordinates to absolute ones
    
    Args:
        annos (list of list):
        types (list of str):
        img_size (tuple): (width, height) of the image in pixels.
    
    Returns:
        list of list: Annotations in absolute format.
    '''
    w, h = img_size
    new = []
    for twod, t in zip(annos,types):
        if t == 'bbox':
            new.append([
                twod[0]*w, twod[1]*h,
                twod[2]*w, twod[3]*h
            ])
        elif t == 'line' or t == 'polygon':
            lp = np.array(twod)
            lp[:,0] = lp[:,0]*w
            lp[:,1] = lp[:,1]*h
            new.append(lp.tolist())
        elif t=='point':
            new.append([twod[0]*w, twod[1]*h])
        else:
            raise Exception('Unknown annotation type: {}'.format(t))
    return np.array(new, dtype=int).tolist()

def calc_box_for_anno(annos, types, point_padding=0.05):
    '''Calculate a bouning box for an arbitrary 2DAnnotation.

    Args:
        annos (list): List of annotations.
        types (list): List of types.
        point_padding (float, optional): In case of a point we need to 
            add some padding to get a box. 

    Returns:
        list: A list of bounding boxes in format [[xc,yc,w,h],...]    
    '''
    new = []
    for anno, t in zip(annos, types):
        if np.max(anno) > 1.0:
            raise ValueError('Annotation are expected to be in relative format! But found: {}'.format(anno))
        if t == 'bbox':
            new.append(anno)
        elif t== 'point':
            new.append([anno[0], anno[1], point_padding, point_padding])
        else:
            lp = np.array(anno)
            xymin = np.min(lp, axis=0)
            xymin[xymin < 0.0] = 0.0
            xmin, ymin = xymin
            xmax, ymax = np.max(lp, axis=0)
            w = xmax - xmin
            h = ymax - ymin
            xc = xmin + w/2.0
            yc = ymin + h/2.0
            new.append([xc, yc, w, h])
    return new

def _add_context(boxes, context, img_size):
    '''Add context around a bounding box.

    Args:
        boxes (list of list of int): Boxes in format [[xmin, ymin, xmax, ymax],...]
        context (float): Context will be calculated reative to the image size.
        img_size (tuple): (width, height) of the image in pixels

    Returns:
        Boxes in absolute format.
    '''
    img_w, img_h = img_size
    old = np.array(boxes)
    new = old.copy()
    wh = np.zeros((len(boxes),2))
    wh = old[:,[2,3]] - old[:,[0,1]]
    new[:,0] -= int(context * img_w)
    new[:,2] += int(context * img_w)
    new[:,1] -= int(context * img_h)
    new[:,3] += int(context * img_h)
    new[new < 0] = 0
    new[:,2][new[:,2] > img_w] = img_w
    new[:,3][new[:,3] > img_h] = img_h
    return new.tolist()

def draw_annos(annos, types, img, color=(255,0,0), point_r=2):
    '''Draw annotations inside a image

    Args:
        annos (list): List of annotations.
        types (list): List of types.
        img (numpy.array): The image to draw annotations in.
        color (tuple): (R,G,B) color that is used for drawing.
    
    Note:
        The given image will be directly edited!

    Returns:
        numpy.array: Image with drawn annotations
    '''
    if annos:
        if len(img.shape) < 3: 
            img = gray2rgb(img)
        img_h, img_w, _ = img.shape
        for anno, t in zip(annos, types):
            if t == 'bbox':
                anno = trans_boxes_to([anno])[0]
                anno = to_abs([anno], [t], (img_w, img_h))[0]
                xmin, ymin, xmax, ymax = anno
                rr, cc = polygon_perimeter([ymin, ymin, ymax, ymax],
                    [xmin, xmax, xmax, xmin ], shape=img.shape)
            elif t == 'polygon':
                anno = to_abs([anno], [t], (img_w, img_h))[0]
                anno = np.array(anno)
                rr, cc = polygon_perimeter(anno[:,1].tolist(),
                    anno[:,0].tolist(), shape=img.shape)
            elif t == 'point':
                anno = to_abs([anno], [t], (img_w, img_h))[0]
                rr, cc = circle(anno[1], anno[0], point_r, shape=img.shape)
            elif t == 'line':
                anno = to_abs([anno], [t], (img_w, img_h))[0]
                for i, point in enumerate(anno):
                    if i >= (len(anno)-1):
                        break
                    rr, cc = line(point[1], point[0], 
                        anno[i+1][1], anno[i+1][0])
                    img[rr,cc] = color
            else:
                raise ValueError('Unknown annotation type: {}'.format(t))
            img[rr,cc] = color
        return img
    else:
        return []

def crop_boxes(annos, types, img, context=0.0, draw_annotations=False):
    '''Crop a bounding boxes for TwoDAnnos from image.
    
    Args:
        annos (list): List of annotations.
        types (list): List of types.
        img (numpy.array): The image where boxes should be cropped from.
        context (float): The context that should be added to the box.
        draw_annotations (bool): If true, annotation will be painted inside
            the crop.
    
    Return:
        (list of numpy.array, list of list of float): 
            A tuple that contains a list of image crops and a 
            list of bboxes [[xc,yc,w,h],...]
    '''
    if annos:
        crops = []
        new_img = img
        anno_boxes = calc_box_for_anno(annos, types)
        boxes = trans_boxes_to(anno_boxes)
        if len(img.shape) < 3:
            img = gray2rgb(img)
        img_h, img_w, _ = img.shape
        boxes = to_abs(boxes, ['bbox']*len(boxes), (img_w,img_h))
        if context != 0.0:
            boxes = _add_context(boxes, context, (img_w, img_h))
        boxes = np.array(boxes, dtype=int).tolist()
        for idx, box in enumerate(boxes):
            if draw_annotations:
                new_img = img.copy()
                draw_annos([annos[idx]], [types[idx]], new_img)
            # image[y_min:y_max, x_min:x_max]
            crops.append(new_img[box[1]:box[3], box[0]:box[2]])
        return crops, anno_boxes
    else:
        return [], []