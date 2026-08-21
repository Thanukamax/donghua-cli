class DonghuaCli < Formula
  include Language::Python::Virtualenv

  desc "Wuxia-themed terminal client for streaming Chinese animation"
  homepage "https://github.com/Thanukamax/donghua-cli"
  # Update URL and sha256 on each release
  url "https://files.pythonhosted.org/packages/c8/ef/2421c2e8915832e95597be5a6b0f526ee92c02a1a7814d9a16b1d5cdf83a/donghua_cli-4.0.0.tar.gz"
  sha256 "65831ea2595da430589c5c0b9e4ddf539e7d6e9da6ddfda2bcf36dbb35931ee5"
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
