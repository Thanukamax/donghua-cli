class DonghuaCli < Formula
  include Language::Python::Virtualenv

  desc "Wuxia-themed terminal client for streaming Chinese animation"
  homepage "https://github.com/Thanukamax/donghua-cli"
  # Update URL and sha256 on each release
  url "https://files.pythonhosted.org/packages/1c/20/d3fab4f7b8029e35d7a05d40686d69f5efb962c446488f1c789a448ca08f/donghua_cli-3.2.1.tar.gz"
  sha256 "3a810fde870cc521f41745673469874915b122e584dc953d9e811343fb72acda"
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
