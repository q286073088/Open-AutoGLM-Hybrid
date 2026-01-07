package com.autoglm.helper

import android.util.Log
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.ServerSocket
import java.net.Socket
import java.net.SocketTimeoutException
import java.util.concurrent.Executors

/**
 * 简单的 HTTP 服务器实现
 * 完全绕过 NanoHTTPD，使用原始 Socket 实现
 * 确保每个请求处理完后立即关闭连接
 */
class SimpleHttpServer(private val service: AutoGLMAccessibilityService, private val port: Int = 8080) {

    companion object {
        private const val TAG = "AutoGLM-SimpleHttpServer"
    }

    private var serverSocket: ServerSocket? = null
    private val executor = Executors.newCachedThreadPool()
    @Volatile
    private var running = false

    fun start() {
        try {
            serverSocket = ServerSocket(port)
            serverSocket?.soTimeout = 0  // 无限等待连接
            running = true

            Log.i(TAG, "HTTP server started on port $port")

            // 在后台线程中接受连接
            executor.execute {
                acceptConnections()
            }

        } catch (e: Exception) {
            Log.e(TAG, "Failed to start HTTP server", e)
            throw e
        }
    }

    fun stop() {
        running = false
        try {
            serverSocket?.close()
            executor.shutdown()
            Log.i(TAG, "HTTP server stopped")
        } catch (e: Exception) {
            Log.e(TAG, "Error stopping server", e)
        }
    }

    private fun acceptConnections() {
        while (running) {
            try {
                val clientSocket = serverSocket?.accept() ?: break
                Log.d(TAG, "Accepted connection from ${clientSocket.inetAddress.hostAddress}")

                // 为每个连接创建一个新线程
                executor.execute {
                    handleClient(clientSocket)
                }

            } catch (e: SocketTimeoutException) {
                // 超时是正常的，继续等待
                continue
            } catch (e: Exception) {
                if (running) {
                    Log.e(TAG, "Error accepting connection", e)
                }
                break
            }
        }
    }

    private fun handleClient(socket: Socket) {
        val clientId = socket.inetAddress.hostAddress + ":" + socket.port
        Log.i(TAG, "[$clientId] Client connected")

        try {
            // 禁用 Nagle 算法，立即发送数据
            socket.tcpNoDelay = true
            Log.d(TAG, "[$clientId] TCP_NODELAY enabled")

            // 设置超时
            socket.soTimeout = 5000  // 5秒读取超时
            Log.d(TAG, "[$clientId] Socket timeout set to 5000ms")

            val inputStream = socket.getInputStream()
            val outputStream = socket.getOutputStream()
            val reader = BufferedReader(InputStreamReader(inputStream))

            // 读取请求行
            Log.d(TAG, "[$clientId] Reading request line...")
            val requestLine = reader.readLine()
            if (requestLine == null) {
                Log.w(TAG, "[$clientId] Request line is null, closing connection")
                return
            }
            Log.i(TAG, "[$clientId] Request: $requestLine")

            val parts = requestLine.split(" ")
            if (parts.size < 3) {
                Log.w(TAG, "[$clientId] Invalid request format")
                sendError(outputStream, 400, "Bad Request")
                outputStream.flush()
                socket.shutdownOutput()
                return
            }

            val method = parts[0]
            val uri = parts[1]
            Log.d(TAG, "[$clientId] Method: $method, URI: $uri")

            // 读取请求头
            Log.d(TAG, "[$clientId] Reading headers...")
            val headers = mutableMapOf<String, String>()
            var line: String?
            var headerCount = 0
            while (reader.readLine().also { line = it } != null) {
                if (line!!.isEmpty()) {
                    Log.d(TAG, "[$clientId] Headers complete, count: $headerCount")
                    break
                }
                headerCount++
                val colonIndex = line!!.indexOf(':')
                if (colonIndex > 0) {
                    val key = line!!.substring(0, colonIndex).trim().lowercase()
                    val value = line!!.substring(colonIndex + 1).trim()
                    headers[key] = value
                    Log.d(TAG, "[$clientId] Header: $key = $value")
                }
            }

            // 读取请求体（如果有）
            var body = ""
            val contentLength = headers["content-length"]?.toIntOrNull() ?: 0
            if (contentLength > 0) {
                Log.d(TAG, "[$clientId] Reading body, content-length: $contentLength")
                val buffer = CharArray(contentLength)
                reader.read(buffer, 0, contentLength)
                body = String(buffer)
                Log.d(TAG, "[$clientId] Body read complete")
            }

            // 处理请求
            Log.d(TAG, "[$clientId] Processing request...")
            val response = handleRequest(method, uri, body)
            Log.d(TAG, "[$clientId] Request processed, status: ${response.statusCode}")

            // 发送响应
            Log.d(TAG, "[$clientId] Sending response...")
            sendResponse(outputStream, response)
            Log.i(TAG, "[$clientId] Response sent successfully")

            // 确保数据发送完毕
            Log.d(TAG, "[$clientId] Flushing output stream...")
            outputStream.flush()
            Log.d(TAG, "[$clientId] Output stream flushed")

            // 关闭输出流，通知客户端数据发送完毕
            Log.d(TAG, "[$clientId] Shutting down output...")
            socket.shutdownOutput()
            Log.d(TAG, "[$clientId] Output shutdown complete")

        } catch (e: Exception) {
            Log.e(TAG, "[$clientId] Error handling client: ${e.message}", e)
        } finally {
            // 确保关闭连接
            try {
                socket.close()
                Log.i(TAG, "[$clientId] Connection closed")
            } catch (e: Exception) {
                Log.e(TAG, "[$clientId] Error closing socket: ${e.message}", e)
            }
        }
    }

    private fun handleRequest(method: String, uri: String, body: String): HttpResponse {
        return try {
            when {
                uri == "/status" && method == "GET" -> handleStatus()
                uri == "/screenshot" && method == "GET" -> handleScreenshot()
                uri == "/tap" && method == "POST" -> handleTap(body)
                uri == "/swipe" && method == "POST" -> handleSwipe(body)
                uri == "/input" && method == "POST" -> handleInput(body)
                else -> HttpResponse(404, "application/json", """{"error": "Not found"}""")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error handling request: $method $uri", e)
            HttpResponse(500, "application/json", """{"error": "${e.message}"}""")
        }
    }

    private fun handleStatus(): HttpResponse {
        val json = JSONObject()
        json.put("status", "ok")
        json.put("service", "AutoGLM Helper")
        json.put("version", "1.0.8")
        json.put("build", "20260107-debug-logs")
        json.put("accessibility_enabled", service.isAccessibilityEnabled())

        return HttpResponse(200, "application/json", json.toString())
    }

    private fun handleScreenshot(): HttpResponse {
        val screenshot = service.takeScreenshotBase64()

        return if (screenshot != null) {
            val json = JSONObject()
            json.put("success", true)
            json.put("image", screenshot)
            json.put("format", "base64")
            HttpResponse(200, "application/json", json.toString())
        } else {
            val json = JSONObject()
            json.put("success", false)
            json.put("error", "Failed to take screenshot")
            HttpResponse(500, "application/json", json.toString())
        }
    }

    private fun handleTap(body: String): HttpResponse {
        val json = JSONObject(body)
        val x = json.getInt("x")
        val y = json.getInt("y")

        val success = service.performTap(x, y)

        val response = JSONObject()
        response.put("success", success)

        return HttpResponse(200, "application/json", response.toString())
    }

    private fun handleSwipe(body: String): HttpResponse {
        val json = JSONObject(body)
        val x1 = json.getInt("x1")
        val y1 = json.getInt("y1")
        val x2 = json.getInt("x2")
        val y2 = json.getInt("y2")
        val duration = json.optInt("duration", 300)

        val success = service.performSwipe(x1, y1, x2, y2, duration)

        val response = JSONObject()
        response.put("success", success)

        return HttpResponse(200, "application/json", response.toString())
    }

    private fun handleInput(body: String): HttpResponse {
        val json = JSONObject(body)
        val text = json.getString("text")

        val success = service.performInput(text)

        val response = JSONObject()
        response.put("success", success)

        return HttpResponse(200, "application/json", response.toString())
    }

    private fun sendResponse(outputStream: java.io.OutputStream, response: HttpResponse) {
        try {
            // 先转换响应体为字节，确保 Content-Length 准确
            val bodyBytes = response.body.toByteArray(Charsets.UTF_8)

            // 构建完整的 HTTP 响应
            val statusLine = "HTTP/1.0 ${response.statusCode} ${getStatusText(response.statusCode)}\r\n"
            val headers = StringBuilder()
            headers.append("Content-Type: ${response.contentType}\r\n")
            headers.append("Content-Length: ${bodyBytes.size}\r\n")
            headers.append("Connection: close\r\n")
            headers.append("Server: AutoGLM-Helper/1.0\r\n")
            headers.append("\r\n")

            // 一次性写入所有数据
            outputStream.write(statusLine.toByteArray(Charsets.UTF_8))
            outputStream.write(headers.toString().toByteArray(Charsets.UTF_8))
            outputStream.write(bodyBytes)

            // 强制刷新到网络
            outputStream.flush()

            Log.d(TAG, "Response sent: ${response.statusCode}, body size: ${bodyBytes.size}")
        } catch (e: Exception) {
            Log.e(TAG, "Error sending response", e)
            throw e  // 重新抛出异常，让调用者知道发送失败
        }
    }

    private fun sendError(outputStream: java.io.OutputStream, statusCode: Int, message: String) {
        val json = JSONObject()
        json.put("error", message)
        sendResponse(outputStream, HttpResponse(statusCode, "application/json", json.toString()))
    }

    private fun getStatusText(statusCode: Int): String {
        return when (statusCode) {
            200 -> "OK"
            400 -> "Bad Request"
            404 -> "Not Found"
            500 -> "Internal Server Error"
            else -> "Unknown"
        }
    }

    data class HttpResponse(
        val statusCode: Int,
        val contentType: String,
        val body: String
    )
}
