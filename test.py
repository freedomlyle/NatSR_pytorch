import argparse

from PIL import Image
import torch
import torch.nn.functional as F
from torchvision.utils import save_image

from model import NSRNet
from utils import ImageSplitter


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', type=str,
                        help='The filename of image to be completed.')
    parser.add_argument('--output', default='output.png', type=str,
                        help='Where to write output.')
    parser.add_argument('--checkpoint', type=str,
                        help='The filename of pickle checkpoint.')
    parser.add_argument('--scale', type=int, default=4, help="scale")
    args = parser.parse_args()

    use_cuda = torch.cuda.is_available()
    device = torch.device('cuda' if use_cuda else 'cpu')

    model = NSRNet(scale=args.scale).to(device)
    checkpoint = torch.load(args.checkpoint, map_location=device)
    model.load_state_dict(checkpoint)
    model.eval()

    splitter = ImageSplitter(scale=args.scale)

    img = Image.open(args.image).convert('RGB')
    patches = splitter.split(img)

    import time
    start_time = time.time()
    out = [model(p.to(device)) for p in patches]
    print("Done in %.3f seconds!" % (time.time() - start_time))

    out_img = splitter.merge(out)
    save_image(out_img, args.output)