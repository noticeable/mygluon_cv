"""Faster RCNN Demo script."""
import os
import argparse
import mxnet as mx
import gluoncv as gcv
from gluoncv.data.transforms import presets
from matplotlib import pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description='Test with Faster RCNN networks.')
    parser.add_argument('--network', type=str, default='faster_rcnn_resnet18_v1b_voc',
                        help="Faster RCNN full network name")
    parser.add_argument('--images', type=str, default='',
                        help='Test images, use comma to split multiple.')
    parser.add_argument('--gpus', type=str, default='0',
                        help='Training with GPUs, you can specify 1,3 for example.')
    parser.add_argument('--pretrained', type=str, default='./baseline/resnet18/baselinefaster_rcnn_resnet18_v1b_voc_best.params',#'./caps/resnet18/caps1_faster_rcnn_caps_resnet18_v1b_voc_best.params',
                        help='Load weights from previously saved parameters. You can specify parameter file name.')
    parser.add_argument('--thresh', type=float, default=0.8,
                        help='Threshold of object score when visualize the bboxes.')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    # context list
    ctx = [mx.gpu(int(i)) for i in args.gpus.split(',') if i.strip()]
    ctx = [mx.cpu()] if not ctx else ctx

    # grab some image if not specified
    if not args.images.strip():
        # gcv.utils.download('https://github.com/dmlc/web-data/blob/master/' +
        #                    'gluoncv/detection/biking.jpg?raw=true', 'biking.jpg')
        path = './a/'
        img_name = os.listdir(path)
    else:
        image_list = [x.strip() for x in args.images.split(',') if x.strip()]

    if args.pretrained.lower() in ['true', '1', 'yes', 't']:
        net = gcv.model_zoo.get_model(args.network, pretrained=True)
    else:
        net = gcv.model_zoo.get_model(args.network, pretrained=False, pretrained_base=False)
        net.load_parameters(args.pretrained)
    net.set_nms(0.3, 200)
    net.collect_params().reset_ctx(ctx = ctx)

    for image in img_name:
        if not image.endswith('.jpg'):
            continue
        ax = None
        x, img = presets.rcnn.load_test(os.path.join(path,image), short=net.short, max_size=net.max_size)
        x = x.as_in_context(ctx[0])
        ids, scores, bboxes = [xx[0].asnumpy() for xx in net(x)]
        ax = gcv.utils.viz.plot_bbox(img, bboxes, scores, ids, thresh=args.thresh,
                                     class_names=net.classes, ax=ax)
        plt.axis('off')
        plt.savefig('./a/results/'+image.split('/')[-1], bbox_inches='tight', dpi=100)
        # plt.show()
        # plt.close()
