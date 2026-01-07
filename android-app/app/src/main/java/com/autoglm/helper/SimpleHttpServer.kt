package com.autoglm.helper

import android.util.Log
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.io.PrintWriter
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
        try {
            // 设置超时
            socket.soTimeout = 5000  // 5秒读取超时

            val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
            val writer = PrintWriter(OutputStreamWriter(socket.getOutputStream()), true)

            // 读取请求行
            val requestLine = reader.readLine() ?: return
            Log.i(TAG, "Request: $requestLine")

            val parts = requestLine.split(" ")
            if (parts.size < 3) {
                sendError(writer, 400, "Bad Request")
                return
            }

            val method = parts[0]
            val uri = parts[1]

            // 读取请求头
            val headers = mutableMapOf<String, String>()
            var line: String?
            while (reader.readLine().also { line = it } != null) {
                if (line!!.isEmpty()) break
                val colonIndex = line!!.indexOf(':')
                if (colonIndex > 0) {
                    val key = line!!.substring(0, colonIndex).trim().lowercase()
                    val value = line!!.substring(colonIndex + 1).trim()
                    headers[key] = value
                }
            }

            // 读取请求体（如果有）
            var body = ""
            val contentLength = headers["content-length"]?.toIntOrNull() ?: 0
            if (contentLength > 0) {
                val buffer = CharArray(contentLength)
                reader.read(buffer, 0, contentLength)
                body = String(buffer)
            }

            // 处理请求
            val response = handleRequest(method, uri, body)

            // 发送响应
            sendResponse(writer, response)

        } catch (e: Exception) {
            Log.e(TAG, "Error handling client", e)
        } finally {
            // 确保关闭连接
            try {
                socket.close()
                Log.d(TAG, "Connection closed")
            } catch (e: Exception) {
                Log.e(TAG, "Error closing socket", e)
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
        json.put("version", "1.0.4")
        json.put("build", "20260107-simple-http")
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

    private fun sendResponse(writer: PrintWriter, response: HttpResponse) {
        val body = response.body.toByteArray(Charsets.UTF_8)

        // 发送状态行
        writer.print("HTTP/1.0 ${response.statusCode} ${getStatusText(response.statusCode)}\r\n")

        // 发送响应头
        writer.print("Content-Type: ${response.contentType}\r\n")
        writer.print("Content-Length: ${body.size}\r\n")
        writer.print("Connection: close\r\n")
        writer.print("Server: AutoGLM-Helper/1.0\r\n")
        writer.print("\r\n")

        // 发送响应体
        writer.print(response.body)
        writer.flush()

        Log.d(TAG, "Response sent: ${response.statusCode}")
    }

    private fun sendError(writer: PrintWriter, statusCode: Int, message: String) {
        val json = JSONObject()
        json.put("error", message)
        sendResponse(writer, HttpResponse(statusCode, "application/json", json.toString()))
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
