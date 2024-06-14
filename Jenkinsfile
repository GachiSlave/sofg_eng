pipeline {

    // Использование Docker в качестве агента
    agent {
        docker {
            // Файл докера расположен в корне репозитория. Образ размещен на dockerhub
            image "kurdt23/sof_eng:car"

            // Предоставление root-прав и монтаж Docker сокета
            args "-u root:sudo -v /var/run/docker.sock:/var/run/docker.sock"
        }
    }

    stages {
        stage('Start') {
            steps {
                script {
                    echo "Начало работы скриптов"
                }
            }
        }

        stage('Checkout') {
            steps {
                script {
                    // Клонирование репозитория Git
                    git branch: 'main', url: 'https://github.com/GachiSlave/sofg_eng'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                // Подключение виртуальной среды
                sh "python3 -m venv venv"
                sh ". venv/bin/activate"

                //  Установка зависимостей
                sh "pip3 install --upgrade pip"
                sh 'pip3 install flake8 dvc-gdrive numpy opencv-python-headless'
                // sh "pip3 install -r requirements.txt"

                // Установка предварительно обученной модели
                // sh "pip3 install gdown"
                // sh "gdown https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -O yolov8n.pt"
            }
        }

        stage('Run linter flake8') {
            steps {
                // Проверка кода литером flake8
                sh "flake8 . --ignore=C901,E402,E501 --count --select=E9,F63,F7,F82 --show-source --statistics --exit-zero --max-complexity=10 --max-line-length=127"
            }
        }

        stage('Install DVC and Sync Data') {
            steps {
                // Копирование секретного файла для DVC
		        withCredentials([file(credentialsId: 'gdrive', variable: 'gdrive')]) {
		            sh "cp \$gdrive $WORKSPACE"
		        }

                 // Модификация удаленного хранилища DVC с использованием секретного файла
                 sh "dvc remote modify myremote --local gdrive_user_credentials_file gdrive.json"

                 // Синхронизация с удалённым хранилищем google-drive
                 sh "dvc pull"
            }
        }

        stage('Run Tests') {
            steps {
                // Установка libgl1 для OpenCV
                sh "apt-get update && apt-get install -y libgl1"

                // Копирование видеофайла
                // sh "cp $WORKSPACE/video.mp4 $WORKSPACE/tests/video.mp4"

                // Запуск модульных тестов и тестов на проверку данных
                sh "python3 -m unittest discover -s $WORKSPACE/tests"
            }
        }

        stage('Build Docker Image') {
            steps {
                // Загрузка Docker in Docker
                sh "apt-get install -y docker.io"

                // Запуск Docker демона в фоновом режиме
                sh "dockerd-entrypoint.sh &"

                // Ожидание готовности Docker демона
                sh "sleep 10"

                // Логин в DockerHub
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'USERNAME',
                    passwordVariable: 'PASSWORD')]) {
                    sh "echo $PASSWORD | docker login -u $USERNAME --password-stdin"
                }

                // Сборка Docker образа
                sh "docker build -t kurdt23/sof_eng:car ."
            }
        }

        stage('Update Config') {
            steps {
                // Установка CHAT_ID для телеграм бота
                withCredentials([string(credentialsId: 'YOUR_CHAT_ID', variable: 'YOUR_CHAT_ID')]) {
                    sh "sed -i 's/chat_id:.*/chat_id: \"${YOUR_CHAT_ID}\"/' config.yaml"
                }
            }
        }

        stage('Run Python Script') {
            steps {
                // Реализация приложения в виде образа Docker
                sh "docker run --rm kurdt23/sof_eng:car"
            }
        }

        stage('Push Docker Image') {
            steps {
                // Пуш Docker образа в DockerHub
                sh "docker push kurdt23/sof_eng:car"
            }
        }

        stage('Finish') {
            steps {
                script {
                    echo "Работа скриптов завершена успешно"
                }
            }
        }
    }
}
