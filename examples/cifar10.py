"""CIFAR10 example for cnn_finetune.
Based on:
- https://github.com/pytorch/tutorials/blob/master/beginner_source/blitz/cifar10_tutorial.py
- https://github.com/pytorch/examples/blob/master/mnist/main.py
"""

import argparse

import torch
import torchvision
import torchvision.transforms as transforms
from torch.autograd import Variable
import torch.nn as nn
import torch.optim as optim
import utils
from cnn_finetune import make_model


parser = argparse.ArgumentParser(description='cnn_finetune cifar 10 example')
parser.add_argument('--batch-size', type=int, default=32, metavar='N',
                    help='input batch size for training (default: 32)')
parser.add_argument('--test-batch-size', type=int, default=64, metavar='N',
                    help='input batch size for testing (default: 64)')
parser.add_argument('--epochs', type=int, default=100, metavar='N',
                    help='number of epochs to train (default: 100)')
parser.add_argument('--lr', type=float, default=0.01, metavar='LR',
                    help='learning rate (default: 0.01)')
parser.add_argument('--momentum', type=float, default=0.9, metavar='M',
                    help='SGD momentum (default: 0.9)')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='disables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=100, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--model-name', type=str, default='resnet50', metavar='M',
                    help='model name (default: resnet50)')
parser.add_argument('--dropout-p', type=float, default=0.2, metavar='D',
                    help='Dropout probability (default: 0.2)')

args = parser.parse_args()
use_cuda = not args.no_cuda and torch.cuda.is_available()
device = torch.device('cuda' if use_cuda else 'cpu')


def train(model, epoch, optimizer, train_loader, criterion=nn.CrossEntropyLoss()):
    total_loss = 0
    total_size = 0
    correct = 0
    train_loss=0
    train_accuracy=0
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        total_loss += loss.item()
        total_size += data.size(0)
        loss.backward()
        optimizer.step()
        pred = output.argmax(dim=1, keepdim=True)
        correct += pred.eq(target.view_as(pred)).sum().item()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tAverage loss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), total_loss / total_size))
    train_loss /= len(train_loader.dataset)
    train_accuracy = 100. * correct / len(train_loader.dataset)
    return train_loss,train_accuracy

def test(model, test_loader, criterion=nn.CrossEntropyLoss()):
    model.eval()
    test_loss = 0
    correct = 0
    test_loss=0
    test_accuracy=0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item()
            pred = output.data.max(1, keepdim=True)[1]
            correct += pred.eq(target.data.view_as(pred)).long().cpu().sum().item()
          
    test_loss /= len(test_loader.dataset)
    test_accuracy = 100. * correct / len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))
    return test_loss,test_accuracy


def main():
    '''Main function to run code in this script'''

    model_name = args.model_name

    if model_name == 'alexnet':
        raise ValueError('The input size of the CIFAR-10 data set (32x32) is too small for AlexNet')

    # classes = (
    #     'plane', 'car', 'bird', 'cat', 'deer',
    #     'dog', 'frog', 'horse', 'ship', 'truck'
    # )
    classes = [f'class{i}' for i in range(100)] 
    model = make_model(
        model_name,
        pretrained=False,
        num_classes=len(classes),
        dropout_p=args.dropout_p,
        input_size=(32, 32) if model_name.startswith(('vgg', 'squeezenet')) else None,
    )
    model = model.to(device)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=model.original_model_info.mean,
            std=model.original_model_info.std),
    ])

    train_set = torchvision.datasets.CIFAR100(
        root='./data', train=True, download=True, transform=transform
    )
    train_loader = torch.utils.data.DataLoader(
        train_set, batch_size=args.batch_size, shuffle=True, num_workers=2
    )
    test_set = torchvision.datasets.CIFAR100(
        root='./data', train=False, download=True, transform=transform
    )
    test_loader = torch.utils.data.DataLoader(
        test_set, args.test_batch_size, shuffle=False, num_workers=2
    )

    optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum)

    # Use exponential decay for fine-tuning optimizer
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=1, gamma=0.975)

    # Train
    for epoch in range(1, args.epochs + 1):
        # Decay Learning Rate
        scheduler.step(epoch)
        train_loss, train_accuracy = train(model, epoch, optimizer, train_loader)
        test_loss , test_accuracy = test(model, test_loader)
        logger.record(epoch, train_loss, test_loss,train_accuracy, test_accuracy)
        # 結果の保存
    folder_name = 'cifar100'
    utils.save(folder_name, logger, model, device,  hyperparams={
        'model_name':args.model_name,
        'batch_size': args.batch_size,
        'learning_rate': args.lr,
        'epochs': args.epochs,
        'optimizer': optimizer,
        'loss_fn': nn.CrossEntropyLoss(),
        'scheduler': scheduler,
    })


if __name__ == '__main__':
    logger = utils.Logger()
    main()
