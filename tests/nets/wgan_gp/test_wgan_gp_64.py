"""
Test functions for WGAN-GP for image size 64.
"""
import torch
import torch.optim as optim

from torch_mimicry.nets.wgan_gp.wgan_gp_64 import WGANGPGenerator64, WGANGPDiscriminator64
from torch_mimicry.training import metric_log
from torch_mimicry.utils import common


class TestWGANGP64:
    def setup(self):
        self.nz = 128
        self.N, self.C, self.H, self.W = (8, 3, 64, 64)
        self.ngf = 16
        self.ndf = 16

        self.netG = WGANGPGenerator64(ngf=self.ngf)
        self.netD = WGANGPDiscriminator64(ndf=self.ndf)

    def test_WGANGPGenerator64(self):
        noise = torch.ones(self.N, self.nz)
        output = self.netG(noise)

        assert output.shape == (self.N, self.C, self.H, self.W)

    def test_WGANGPDiscriminator64(self):
        images = torch.ones(self.N, self.C, self.H, self.W)
        output = self.netD(images)

        assert output.shape == (self.N, 1)

    def test_train_steps(self):
        # Get real and fake images
        real_batch = common.load_images(self.N, size=self.H)

        # Setup optimizers
        optD = optim.Adam(self.netD.parameters(), 2e-4, betas=(0.0, 0.9))
        optG = optim.Adam(self.netG.parameters(), 2e-4, betas=(0.0, 0.9))

        # Log statistics to check
        log_data = metric_log.MetricLog()

        # Test D train step
        log_data = self.netD.train_step(real_batch=real_batch,
                                        netG=self.netG,
                                        optD=optD,
                                        device='cpu',
                                        log_data=log_data)

        log_data = self.netG.train_step(real_batch=real_batch,
                                        netD=self.netD,
                                        optG=optG,
                                        log_data=log_data,
                                        device='cpu')

        for name, metric_dict in log_data.items():
            assert type(name) == str
            assert type(metric_dict['value']) == float

    def teardown(self):
        del self.netG
        del self.netD


if __name__ == "__main__":
    test = TestWGANGP64()
    test.setup()
    test.test_WGANGPGenerator64()
    test.test_WGANGPDiscriminator64()
    test.test_train_steps()
    test.teardown()
