//자바스크립트 버전
const mysql = require('mysql');
const openai = require('openai'); // OpenAI API 라이브러리

// 데이터베이스 연결 설정
const dbConfig = {
  host: 'localhost',
  user: 'username',
  password: 'password',
  database: 'database_name',
};

// OpenAI API 인증 설정
const openaiConfig = {
  apiKey: 'your_openai_api_key',
};

// 데이터베이스 연결 생성
const connection = mysql.createConnection(dbConfig);

// OpenAI API 클라이언트 생성
const openaiClient = new openai.LanguageCompletionClient(openaiConfig.apiKey);

// 데이터베이스에서 데이터 가져오고 요약 처리 후 저장하는 함수
function summarizeData() {
  connection.connect((err) => {
    if (err) {
      console.error('Database connection error:', err);
      return;
    }

    // 데이터베이스 쿼리 실행
    const query = 'SELECT contacts FROM chat';
    connection.query(query, (err, results) => {
      if (err) {
        console.error('Database query error:', err);
        connection.end();
        return;
      }

      // 가져온 데이터를 OpenAI로 요약 처리
      const contacts = results.map((row) => row.contacts);
      const summaries = contacts.map((contact) => {
        // OpenAI API 호출
        const prompt = `Summarize: ${contact}`;
        const options = {
          temperature: 0.5,
          maxTokens: 100,
        };

        return openaiClient.complete(prompt, options)
          .then((response) => response.choices[0].text.trim())
          .catch((err) => {
            console.error('OpenAI API error:', err);
            return '';
          });
      });

      // 요약된 내용을 데이터베이스에 저장
      const updateQuery = 'UPDATE chat SET summary = ? WHERE contacts = ?';
      summaries.forEach((summary, index) => {
        connection.query(updateQuery, [summary, contacts[index]], (err) => {
          if (err) {
            console.error('Database update error:', err);
          }
        });
      });

      connection.end();
    });
  });
}

// summarizeData 함수 실행
summarizeData();
