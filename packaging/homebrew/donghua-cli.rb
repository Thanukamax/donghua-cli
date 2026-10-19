class DonghuaCli < Formula
  include Language::Python::Virtualenv

  desc "Wuxia-themed terminal client for streaming Chinese animation"
  homepage "https://github.com/Thanukamax/donghua-cli"
  # Update URL and sha256 on each release
  url "https://files.pythonhosted.org/packages/c3/4c/1e2ee041ab061716dd444afb7f2d408d779597cce34a5f313240f9bef36b/donghua_cli-4.1.0.tar.gz"
  sha256 "187b93d41c7c8e622e6f371056c2aba5f3d0d82ad6b48423ad16a46a1ecae0f4"
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
