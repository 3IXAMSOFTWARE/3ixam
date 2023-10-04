#include "../include/time_bomb/time_bomb.h"

#include <boost/beast/core.hpp>
#include <boost/beast/http.hpp>
#include <boost/beast/version.hpp>
#include <boost/asio/ssl/error.hpp>
#include <boost/asio/ssl/stream.hpp>
#include <boost/asio/connect.hpp>
#include <boost/asio/ip/tcp.hpp>
#include <boost/asio/ssl.hpp>
#include <cstdlib>
#include <iostream>
#include <string>

#include "CLG_log.h"

#include "BKE_appdir.h"
#include "BLI_fileops.h"
#include "BLI_path_util.h"

bool validateAuthToken(const char* auth_token)
{
  char filepath[FILENAME_MAX] = {'\0'};
  const char *group_path = BKE_appdir_folder_id(IXAM_SYSTEM_GROUP, "Library");
  char res[FILENAME_MAX] = {'\0'};

  BLI_path_join(filepath, sizeof(filepath), group_path, "Application Support", "3ixam", "preferences");

  FILE *file = fopen(filepath, "rb");
  if (file != nullptr) {
    char *readed =  fgets(res, sizeof(res), file);
    if (readed != NULL && strcmp(res, IXAM_LAUNCH_FILE_CONTENT) == 0) {
      fclose(file);
      BLI_delete(filepath, false, false);
      return true;
    }
  }
  return false;
}

int timeBomb(void)
{
  static CLG_LogRef LOG = {"ixam.time_bomb.check"};
  
  namespace beast = boost::beast;
  namespace http = beast::http;
  namespace net = boost::asio;
  namespace ssl = boost::asio::ssl;
  using tcp = net::ip::tcp;

  try {
    const std::string host("api.3ixam.com");
    const std::string port("443");
    const std::string target("/activation");

    net::io_context ioc;

    ssl::context ssl_context(ssl::context::sslv23);
    ssl_context.set_default_verify_paths();
    
    ssl::stream<tcp::socket> socket{ioc, ssl_context};
    socket.set_verify_mode(net::ssl::verify_peer);

    if (!SSL_set_tlsext_host_name(socket.native_handle(), (void *)host.data())) {
      return 0;
    }

    http::request<http::string_body> req{http::verb::get, target, 11};
    req.set(http::field::host, host);
    req.set(http::field::user_agent, BOOST_BEAST_VERSION_STRING);

    tcp::resolver resolver{ioc};
    auto const results = resolver.resolve(host, port);
    net::connect(socket.next_layer(), results.begin(), results.end());
    socket.handshake(ssl::stream_base::client);

    http::write(socket, req);
    
    beast::error_code  ec;
    boost::beast::flat_buffer buffer;
    http::response<http::string_body> res;
    http::read(socket, buffer, res, ec);
    if (ec || res.result() != http::status::ok) {
      return 0;
    }
    
    return atoi(res.body().data());
  }
  catch(std::exception const& e) {
    CLOG_ERROR(&LOG, "ERROR: '%s'", e.what());
  }
  return 0;
}
