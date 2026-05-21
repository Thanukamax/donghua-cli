class DonghuaCli < Formula
  include Language::Python::Virtualenv

  desc "Wuxia-themed terminal client for streaming Chinese animation"
  homepage "https://github.com/Thanukamax/donghua-cli"
  # Update URL and sha256 on each release
  url "https://files.pythonhosted.org/packages/21/2d/3ca89831268b8c9348f3c95fee40e5ddd5d3e3584306d60966802bd9d7ee/donghua_cli-3.2.0.tar.gz"
  sha256 "fc6f2a9d1fb1542ca8f616963fdf18ef49cb363982feece6989aa432f4d0b9c8"
  license "MIT"

  depends_on "python@3.12"
  depends_on "mpv" => :recommended

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "donghua-cli", shell_output("#{bin}/donghua --version")
  end
end
